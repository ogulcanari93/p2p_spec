from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import PaymentRequest, RequestEvent, User
from app.schemas import (
    DestinationSnapshotOut,
    PaymentRequestDetailOut,
    PaymentRequestSummaryOut,
    RequestEventOut,
    SenderOut,
)
from app.services.payment_requests import parse_destination_snapshot, share_url


def _as_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _is_expired(request: PaymentRequest, now: datetime | None = None) -> bool:
    now = _as_utc(now or datetime.now(timezone.utc))
    expires = _as_utc(request.expires_at)
    return request.status == "PENDING" and expires <= now


def request_to_summary(
    request: PaymentRequest,
    *,
    viewer: User,
    sender_email: str | None = None,
) -> PaymentRequestSummaryOut:
    snap = parse_destination_snapshot(request)
    expired = _is_expired(request)
    is_sender = request.sender_user_id == viewer.id
    is_recipient = bool(
        request.recipient_user_id == viewer.id
        or request.recipient_contact_hash == viewer.email_hash
        or (
            viewer.phone_hash is not None
            and request.recipient_contact_hash == viewer.phone_hash
        )
    )

    counterparty = request.recipient_contact
    if not is_sender and sender_email:
        counterparty = sender_email

    status = request.status
    can_pay = is_recipient and status == "PENDING" and not expired
    can_decline = is_recipient and status == "PENDING" and not expired
    can_cancel = is_sender and status == "PENDING" and not expired

    return PaymentRequestSummaryOut(
        id=request.id,
        reference_code=request.reference_code,
        share_token=request.share_token,
        status=status,  # type: ignore[arg-type]
        amount_minor=request.amount_minor,
        currency=request.currency,
        note=request.note,
        recipient_contact=request.recipient_contact,
        recipient_contact_type=request.recipient_contact_type,  # type: ignore[arg-type]
        counterparty_label=counterparty,
        destination_snapshot=DestinationSnapshotOut(**snap),
        created_at=request.created_at,
        expires_at=request.expires_at,
        is_expired=expired or status == "EXPIRED",
        can_pay=can_pay,
        can_decline=can_decline,
        can_cancel=can_cancel,
    )


def request_to_detail(
    db: Session,
    request: PaymentRequest,
    *,
    viewer: User,
    sender: User | None = None,
) -> PaymentRequestDetailOut:
    sender_user = sender
    if not sender_user:
        sender_user = db.get(User, request.sender_user_id)
    summary = request_to_summary(
        request,
        viewer=viewer,
        sender_email=sender_user.email if sender_user else None,
    )
    events = list(
        db.execute(
            select(RequestEvent)
            .where(RequestEvent.payment_request_id == request.id)
            .order_by(RequestEvent.created_at.asc())
        ).scalars().all()
    )

    data = summary.model_dump()
    data.update(
        {
            "sender": SenderOut.model_validate(sender_user) if sender_user else None,
            "recipient_user_id": request.recipient_user_id,
            "paid_at": request.paid_at,
            "declined_at": request.declined_at,
            "cancelled_at": request.cancelled_at,
            "expired_at": request.expired_at,
            "share_url": share_url(request.share_token),
            "events": [RequestEventOut.model_validate(event) for event in events],
        }
    )
    return PaymentRequestDetailOut(**data)
