from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import PaymentRequest, PaymentRequestStatus, RequestEventType, User
from app.services.events import record_event


def expire_pending_for_user(db: Session, user: User) -> int:
    now = datetime.now(timezone.utc)
    stmt = select(PaymentRequest).where(
        PaymentRequest.status == PaymentRequestStatus.PENDING.value,
        PaymentRequest.expires_at <= now,
        (
            (PaymentRequest.sender_user_id == user.id)
            | (PaymentRequest.recipient_user_id == user.id)
        ),
    )
    requests = db.execute(stmt).scalars().all()
    count = 0
    for req in requests:
        previous = req.status
        req.status = PaymentRequestStatus.EXPIRED.value
        req.expired_at = now
        record_event(
            db,
            payment_request_id=req.id,
            event_type=RequestEventType.REQUEST_EXPIRED,
            previous_status=previous,
            new_status=req.status,
        )
        count += 1
    if count:
        db.commit()
    return count
