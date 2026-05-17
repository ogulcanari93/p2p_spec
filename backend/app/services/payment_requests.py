import json
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import or_, select, update
from sqlalchemy.orm import Session

from app.config import settings
from app.models import (
    PaymentDestination,
    PaymentRequest,
    PaymentRequestStatus,
    RequestEventType,
    User,
    Wallet,
    WalletTransaction,
    WalletTransactionDirection,
)
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


def _incoming_conditions(viewer: User):
    conditions = [
        PaymentRequest.recipient_user_id == viewer.id,
        PaymentRequest.recipient_contact_hash == viewer.email_hash,
    ]
    if viewer.phone_hash:
        conditions.append(PaymentRequest.recipient_contact_hash == viewer.phone_hash)
    return or_(*conditions)


def _apply_status_filter(stmt, status: str | None):
    if status and status.lower() != "all":
        return stmt.where(PaymentRequest.status == status.upper())
    return stmt


def _apply_search(stmt, search: str | None):
    if not search or not search.strip():
        return stmt
    term = f"%{search.strip().lower()}%"
    return stmt.where(
        or_(
            PaymentRequest.recipient_contact.ilike(term),
            PaymentRequest.note.ilike(term),
            User.email.ilike(term),
        )
    )


def list_payment_requests(
    db: Session,
    viewer: User,
    *,
    direction: str = "all",
    status: str | None = "all",
    search: str | None = None,
) -> tuple[list[PaymentRequest], list[PaymentRequest]]:
    """Return (outgoing, incoming) payment requests for the viewer."""
    outgoing: list[PaymentRequest] = []
    incoming: list[PaymentRequest] = []

    if direction in ("outgoing", "all"):
        stmt = (
            select(PaymentRequest)
            .join(User, PaymentRequest.sender_user_id == User.id)
            .where(PaymentRequest.sender_user_id == viewer.id)
            .order_by(PaymentRequest.created_at.desc())
        )
        stmt = _apply_status_filter(stmt, status)
        stmt = _apply_search(stmt, search)
        outgoing = list(db.execute(stmt).unique().scalars().all())

    if direction in ("incoming", "all"):
        stmt = (
            select(PaymentRequest)
            .join(User, PaymentRequest.sender_user_id == User.id)
            .where(_incoming_conditions(viewer))
            .order_by(PaymentRequest.created_at.desc())
        )
        stmt = _apply_status_filter(stmt, status)
        stmt = _apply_search(stmt, search)
        incoming = list(db.execute(stmt).unique().scalars().all())

    return outgoing, incoming


def list_outgoing_requests(db: Session, sender: User) -> list[PaymentRequest]:
    outgoing, _ = list_payment_requests(db, sender, direction="outgoing")
    return outgoing


def is_recipient(request: PaymentRequest, user: User) -> bool:
    return bool(
        request.recipient_user_id == user.id
        or request.recipient_contact_hash == user.email_hash
        or (user.phone_hash is not None and request.recipient_contact_hash == user.phone_hash)
    )


def _as_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def is_request_expired(request: PaymentRequest, now: datetime | None = None) -> bool:
    now = _as_utc(now or datetime.now(timezone.utc))
    expires = _as_utc(request.expires_at)
    return request.status == PaymentRequestStatus.PENDING.value and expires <= now


def pay_payment_request(db: Session, request_id: str, payer: User) -> PaymentRequest:
    request = db.get(PaymentRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Payment request not found.")

    if request.sender_user_id == payer.id:
        raise HTTPException(status_code=403, detail="You cannot pay your own payment request.")

    if not is_recipient(request, payer):
        raise HTTPException(status_code=403, detail="Only the recipient can pay this request.")

    now = datetime.now(timezone.utc)

    if request.status == PaymentRequestStatus.PAID.value:
        raise HTTPException(status_code=409, detail="This payment request has already been paid.")

    if request.status != PaymentRequestStatus.PENDING.value:
        raise HTTPException(
            status_code=422,
            detail=f"Cannot pay a request with status {request.status}.",
        )

    if is_request_expired(request, now):
        raise HTTPException(status_code=422, detail="This payment request has expired.")

    existing_credit = db.execute(
        select(WalletTransaction).where(
            WalletTransaction.payment_request_id == request_id,
            WalletTransaction.direction == WalletTransactionDirection.CREDIT.value,
        )
    ).scalar_one_or_none()
    if existing_credit:
        raise HTTPException(status_code=409, detail="This payment request has already been paid.")

    previous_status = request.status
    update_result = db.execute(
        update(PaymentRequest)
        .where(
            PaymentRequest.id == request_id,
            PaymentRequest.status == PaymentRequestStatus.PENDING.value,
        )
        .values(
            status=PaymentRequestStatus.PAID.value,
            paid_at=now,
            updated_at=now,
        )
    )
    if update_result.rowcount == 0:
        db.refresh(request)
        if request.status == PaymentRequestStatus.PAID.value:
            raise HTTPException(status_code=409, detail="This payment request has already been paid.")
        raise HTTPException(
            status_code=422,
            detail=f"Cannot pay a request with status {request.status}.",
        )

    db.refresh(request)

    destination = db.get(PaymentDestination, request.destination_id)
    if not destination:
        raise HTTPException(status_code=422, detail="Payment destination is no longer available.")

    if destination.destination_type == "INTERNAL_WALLET" and destination.wallet_id:
        wallet = db.get(Wallet, destination.wallet_id)
        if not wallet:
            raise HTTPException(status_code=422, detail="Sender wallet is not available.")
        if wallet.status != "ACTIVE":
            raise HTTPException(status_code=422, detail="Sender wallet is not active.")

        wallet.balance_minor += request.amount_minor
        wallet.available_balance_minor += request.amount_minor
        wallet.updated_at = now

        db.add(
            WalletTransaction(
                id=str(uuid.uuid4()),
                wallet_id=wallet.id,
                payment_request_id=request.id,
                direction=WalletTransactionDirection.CREDIT.value,
                amount_minor=request.amount_minor,
                currency=request.currency,
                status="POSTED",
                description=f"Payment received for request {request.id[:8]}",
                created_at=now,
            )
        )

    record_event(
        db,
        payment_request_id=request.id,
        event_type=RequestEventType.REQUEST_PAID,
        actor_user_id=payer.id,
        previous_status=previous_status,
        new_status=PaymentRequestStatus.PAID.value,
        metadata={
            "amount_minor": request.amount_minor,
            "currency": request.currency,
            "direction": WalletTransactionDirection.CREDIT.value,
        },
    )

    db.commit()
    db.refresh(request)
    return request


def share_url(share_token: str) -> str:
    base = settings.app_base_url.rstrip("/")
    return f"{base}/r/{share_token}"


def parse_destination_snapshot(request: PaymentRequest) -> dict:
    return json.loads(request.destination_snapshot_json)
