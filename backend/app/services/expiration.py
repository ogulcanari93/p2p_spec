from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import PaymentRequest, PaymentRequestStatus, RequestEventType, User
from app.services.events import record_event


def _as_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def incoming_conditions_for_user(viewer: User):
    """Match incoming requests by linked user id or contact hash (email/phone)."""
    conditions = [
        PaymentRequest.recipient_user_id == viewer.id,
        PaymentRequest.recipient_contact_hash == viewer.email_hash,
    ]
    if viewer.phone_hash:
        conditions.append(PaymentRequest.recipient_contact_hash == viewer.phone_hash)
    return or_(*conditions)


def expire_request_if_due(
    db: Session,
    request: PaymentRequest,
    *,
    now: datetime | None = None,
) -> bool:
    """Transition PENDING → EXPIRED when now >= expires_at. Returns True if expired."""
    now = _as_utc(now or datetime.now(timezone.utc))
    if request.status != PaymentRequestStatus.PENDING.value:
        return False
    if _as_utc(request.expires_at) > now:
        return False

    previous_status = request.status
    request.status = PaymentRequestStatus.EXPIRED.value
    request.expired_at = now
    request.updated_at = now
    record_event(
        db,
        payment_request_id=request.id,
        event_type=RequestEventType.REQUEST_EXPIRED,
        actor_user_id=None,
        previous_status=previous_status,
        new_status=request.status,
    )
    return True


def expire_pending_for_user(db: Session, user: User) -> int:
    """Expire all due PENDING requests visible to the user (sender or recipient)."""
    now = datetime.now(timezone.utc)
    stmt = select(PaymentRequest).where(
        PaymentRequest.status == PaymentRequestStatus.PENDING.value,
        PaymentRequest.expires_at <= now,
        or_(
            PaymentRequest.sender_user_id == user.id,
            incoming_conditions_for_user(user),
        ),
    )
    requests = db.execute(stmt).scalars().all()
    count = 0
    for req in requests:
        if expire_request_if_due(db, req, now=now):
            count += 1
    if count:
        db.commit()
    return count


def expire_pending_for_share_token(db: Session, share_token: str) -> PaymentRequest | None:
    """Expire a share-linked request if due (public read path)."""
    request = db.execute(
        select(PaymentRequest).where(PaymentRequest.share_token == share_token)
    ).scalar_one_or_none()
    if not request:
        return None
    if expire_request_if_due(db, request):
        db.commit()
        db.refresh(request)
    return request
