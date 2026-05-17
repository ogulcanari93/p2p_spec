"""Seed demo users, wallets, destinations, and sample payment requests."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.database import SessionLocal, init_db
from app.models import PaymentRequest, PaymentRequestStatus, RequestEventType, User
from app.services import security
from app.services.events import record_event
from app.services.payment_destinations import ensure_default_destination
import secrets

from app.services.security import build_destination_snapshot, snapshot_to_json
from app.services.wallets import ensure_default_wallet

NOW = datetime.now(timezone.utc)


def _user(
    db,
    *,
    email: str,
    display_name: str,
    phone: str | None = None,
) -> User:
    normalized = email.strip().lower()
    email_hash = security.hash_value(normalized)
    existing = db.execute(select(User).where(User.email_hash == email_hash)).scalar_one_or_none()
    if existing:
        return existing

    phone_hash = security.hash_value(phone) if phone else None
    user = User(
        id=str(uuid.uuid4()),
        email=normalized,
        email_hash=email_hash,
        display_name=display_name,
        phone=phone,
        phone_hash=phone_hash,
    )
    db.add(user)
    db.flush()
    ensure_default_wallet(db, user)
    ensure_default_destination(db, user)
    return user


def _request(
    db,
    *,
    sender: User,
    recipient_contact: str,
    recipient_user: User | None,
    amount_minor: int,
    status: str,
    note: str | None = None,
    expires_at: datetime | None = None,
    paid_at: datetime | None = None,
    declined_at: datetime | None = None,
    cancelled_at: datetime | None = None,
    expired_at: datetime | None = None,
) -> PaymentRequest:
    contact_type = security.detect_contact_type(recipient_contact)
    normalized = security.normalize_contact(recipient_contact, contact_type)
    r_hash = security.contact_hash(recipient_contact, contact_type)
    destination = ensure_default_destination(db, sender)
    snapshot = build_destination_snapshot(destination)
    created = NOW - timedelta(days=2)
    expires = expires_at or (created + timedelta(days=7))

    req = PaymentRequest(
        id=str(uuid.uuid4()),
        share_token=secrets.token_urlsafe(16),
        sender_user_id=sender.id,
        recipient_user_id=recipient_user.id if recipient_user else None,
        recipient_contact=normalized if contact_type.value == "EMAIL" else recipient_contact.strip(),
        recipient_contact_hash=r_hash,
        recipient_contact_type=contact_type.value,
        destination_id=destination.id,
        destination_snapshot_json=snapshot_to_json(snapshot),
        amount_minor=amount_minor,
        currency="TRY",
        note=note,
        status=status,
        created_at=created,
        updated_at=NOW,
        expires_at=expires,
        paid_at=paid_at,
        declined_at=declined_at,
        cancelled_at=cancelled_at,
        expired_at=expired_at,
    )
    db.add(req)
    db.flush()

    record_event(
        db,
        payment_request_id=req.id,
        event_type=RequestEventType.REQUEST_CREATED,
        actor_user_id=sender.id,
        previous_status=None,
        new_status=PaymentRequestStatus.PENDING.value,
    )
    if status == PaymentRequestStatus.PAID.value:
        record_event(
            db,
            payment_request_id=req.id,
            event_type=RequestEventType.REQUEST_PAID,
            actor_user_id=recipient_user.id if recipient_user else None,
            previous_status=PaymentRequestStatus.PENDING.value,
            new_status=status,
        )
    elif status == PaymentRequestStatus.DECLINED.value:
        record_event(
            db,
            payment_request_id=req.id,
            event_type=RequestEventType.REQUEST_DECLINED,
            actor_user_id=recipient_user.id if recipient_user else None,
            previous_status=PaymentRequestStatus.PENDING.value,
            new_status=status,
        )
    elif status == PaymentRequestStatus.CANCELLED.value:
        record_event(
            db,
            payment_request_id=req.id,
            event_type=RequestEventType.REQUEST_CANCELLED,
            actor_user_id=sender.id,
            previous_status=PaymentRequestStatus.PENDING.value,
            new_status=status,
        )
    elif status == PaymentRequestStatus.EXPIRED.value:
        record_event(
            db,
            payment_request_id=req.id,
            event_type=RequestEventType.REQUEST_EXPIRED,
            actor_user_id=None,
            previous_status=PaymentRequestStatus.PENDING.value,
            new_status=status,
        )
    return req


def seed() -> None:
    init_db()
    db = SessionLocal()
    try:
        ogulcan = _user(db, email="ogulcan@example.com", display_name="Ogulcan")
        ayca = _user(db, email="ayca@example.com", display_name="Ayca")
        mehmet = _user(
            db,
            email="mehmet@example.com",
            display_name="Mehmet",
            phone="+905551234567",
        )

        _request(
            db,
            sender=ogulcan,
            recipient_contact="ayca@example.com",
            recipient_user=ayca,
            amount_minor=15000,
            status=PaymentRequestStatus.PENDING.value,
            note="Dinner split",
        )
        _request(
            db,
            sender=ayca,
            recipient_contact="ogulcan@example.com",
            recipient_user=ogulcan,
            amount_minor=5000,
            status=PaymentRequestStatus.PENDING.value,
            note="Coffee",
        )
        _request(
            db,
            sender=ogulcan,
            recipient_contact="ayca@example.com",
            recipient_user=ayca,
            amount_minor=25000,
            status=PaymentRequestStatus.PAID.value,
            note="Paid request",
            paid_at=NOW - timedelta(days=1),
        )
        _request(
            db,
            sender=mehmet,
            recipient_contact="ogulcan@example.com",
            recipient_user=ogulcan,
            amount_minor=7500,
            status=PaymentRequestStatus.DECLINED.value,
            note="Declined sample",
            declined_at=NOW - timedelta(hours=12),
        )
        _request(
            db,
            sender=ogulcan,
            recipient_contact="ayca@example.com",
            recipient_user=ayca,
            amount_minor=3000,
            status=PaymentRequestStatus.CANCELLED.value,
            note="Cancelled sample",
            cancelled_at=NOW - timedelta(hours=6),
        )
        _request(
            db,
            sender=ayca,
            recipient_contact="ogulcan@example.com",
            recipient_user=ogulcan,
            amount_minor=12000,
            status=PaymentRequestStatus.EXPIRED.value,
            note="Expired sample",
            expires_at=NOW - timedelta(days=2),
            expired_at=NOW - timedelta(days=1),
        )
        _request(
            db,
            sender=ogulcan,
            recipient_contact="+905551234567",
            recipient_user=mehmet,
            amount_minor=9900,
            status=PaymentRequestStatus.PENDING.value,
            note="Phone recipient sample",
        )

        db.commit()
        print("Seed complete. Demo users:")
        print("  ogulcan@example.com, ayca@example.com, mehmet@example.com (+905551234567)")
        print("Sample share URL (first pending ogulcan→ayca): log in and open dashboard.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
