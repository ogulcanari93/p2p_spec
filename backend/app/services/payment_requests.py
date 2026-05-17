import json
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import PaymentDestination, PaymentRequest, PaymentRequestStatus, RequestEventType, User
from app.services import security
from app.services.events import record_event
from app.services.money import MoneyValidationError, normalize_currency, parse_amount_to_minor
from app.services.payment_destinations import (
    get_default_destination,
    get_destination_for_user,
)


def assert_pending_transition(current: str, target: str) -> None:
    allowed = {
        PaymentRequestStatus.PENDING.value: {
            PaymentRequestStatus.PAID.value,
            PaymentRequestStatus.DECLINED.value,
            PaymentRequestStatus.CANCELLED.value,
            PaymentRequestStatus.EXPIRED.value,
        }
    }
    if current not in allowed or target not in allowed.get(current, set()):
        raise HTTPException(status_code=422, detail=f"Cannot transition from {current} to {target}.")


def _resolve_recipient_user_id(db: Session, contact_hash: str) -> str | None:
    stmt = select(User).where(
        (User.email_hash == contact_hash) | (User.phone_hash == contact_hash)
    )
    user = db.execute(stmt).scalar_one_or_none()
    return user.id if user else None


def create_payment_request(
    db: Session,
    sender: User,
    *,
    recipient_contact: str,
    amount: str,
    currency: str = "TRY",
    note: str | None = None,
    destination_id: str | None = None,
) -> PaymentRequest:
    try:
        currency_code = normalize_currency(currency)
        amount_minor = parse_amount_to_minor(amount, currency_code)
    except MoneyValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    try:
        contact_type = security.detect_contact_type(recipient_contact)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    normalized_contact = security.normalize_contact(recipient_contact, contact_type)
    r_hash = security.contact_hash(recipient_contact, contact_type)

    if destination_id:
        destination = get_destination_for_user(db, sender, destination_id)
        if not destination:
            raise HTTPException(status_code=403, detail="Payment destination not found or not owned by you.")
    else:
        destination = get_default_destination(db, sender, currency_code)
        if not destination:
            raise HTTPException(
                status_code=422,
                detail="No active payment destination available for this currency.",
            )

    if destination.status != "ACTIVE":
        raise HTTPException(status_code=422, detail="Payment destination is not active.")
    if destination.currency != currency_code:
        raise HTTPException(status_code=422, detail="Destination currency does not match request currency.")

    now = datetime.now(timezone.utc)
    share_token = secrets.token_urlsafe(16)
    snapshot = security.build_destination_snapshot(destination)

    request = PaymentRequest(
        id=str(uuid.uuid4()),
        share_token=share_token,
        sender_user_id=sender.id,
        recipient_user_id=_resolve_recipient_user_id(db, r_hash),
        recipient_contact=normalized_contact if contact_type.value == "EMAIL" else recipient_contact.strip(),
        recipient_contact_hash=r_hash,
        recipient_contact_type=contact_type.value,
        destination_id=destination.id,
        destination_snapshot_json=security.snapshot_to_json(snapshot),
        amount_minor=amount_minor,
        currency=currency_code,
        note=note,
        status=PaymentRequestStatus.PENDING.value,
        created_at=now,
        updated_at=now,
        expires_at=now + timedelta(days=7),
    )
    db.add(request)
    db.flush()

    record_event(
        db,
        payment_request_id=request.id,
        event_type=RequestEventType.REQUEST_CREATED,
        actor_user_id=sender.id,
        previous_status=None,
        new_status=request.status,
    )
    db.commit()
    db.refresh(request)
    return request


def list_outgoing_requests(db: Session, sender: User) -> list[PaymentRequest]:
    stmt = (
        select(PaymentRequest)
        .where(PaymentRequest.sender_user_id == sender.id)
        .order_by(PaymentRequest.created_at.desc())
    )
    return list(db.execute(stmt).scalars().all())


def share_url(share_token: str) -> str:
    base = settings.app_base_url.rstrip("/")
    return f"{base}/r/{share_token}"


def parse_destination_snapshot(request: PaymentRequest) -> dict:
    return json.loads(request.destination_snapshot_json)
