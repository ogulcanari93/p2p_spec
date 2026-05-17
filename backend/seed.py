"""Deterministic demo seed — reset with: python seed.py --reset"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from app.database import Base, SessionLocal, engine, init_db
from app.models import PaymentRequest, PaymentRequestStatus, RequestEventType, User
from app.services import security
from app.services.events import record_event
from app.services.payment_destinations import ensure_default_destination
from app.services.security import DEFAULT_PASSWORD, build_destination_snapshot, snapshot_to_json
from app.services.users import ensure_user
from app.services.wallets import ensure_default_wallet

NOW = datetime.now(timezone.utc)

USER_IDS = {
    "ogulcan@example.com": "11111111-1111-4111-8111-111111111101",
    "ayca@example.com": "11111111-1111-4111-8111-111111111102",
    "mehmet@example.com": "11111111-1111-4111-8111-111111111103",
}


def reset_database() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def _user(
    db,
    *,
    email: str,
    display_name: str,
    phone: str | None = None,
) -> User:
    normalized = email.strip().lower()
    user = ensure_user(
        db,
        email=normalized,
        display_name=display_name,
        phone=phone,
        password=DEFAULT_PASSWORD,
        user_id=USER_IDS[normalized],
    )
    wallet = ensure_default_wallet(db, user)
    if normalized == "ayca@example.com":
        wallet.balance_minor = 500_000
        wallet.available_balance_minor = 500_000
    elif normalized == "ogulcan@example.com":
        wallet.balance_minor = 100_000
        wallet.available_balance_minor = 100_000
    elif normalized == "mehmet@example.com":
        wallet.balance_minor = 200_000
        wallet.available_balance_minor = 200_000
    return user


def _request(
    db,
    *,
    request_id: str,
    reference_code: str,
    share_token: str,
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
        id=request_id,
        reference_code=reference_code,
        share_token=share_token,
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


def seed(*, reset: bool = False) -> None:
    if reset:
        reset_database()
    else:
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

        day = NOW.strftime("%Y%m%d")
        _request(
            db,
            request_id="22222222-2222-4222-8222-222222222201",
            reference_code=f"PR-{day}-0001",
            share_token="seed-share-pending-ogulcan-ayca",
            sender=ogulcan,
            recipient_contact="ayca@example.com",
            recipient_user=ayca,
            amount_minor=15000,
            status=PaymentRequestStatus.PENDING.value,
            note="Dinner split",
        )
        _request(
            db,
            request_id="22222222-2222-4222-8222-222222222202",
            reference_code=f"PR-{day}-0002",
            share_token="seed-share-pending-ayca-ogulcan",
            sender=ayca,
            recipient_contact="ogulcan@example.com",
            recipient_user=ogulcan,
            amount_minor=5000,
            status=PaymentRequestStatus.PENDING.value,
            note="E2E decline target",
        )
        _request(
            db,
            request_id="22222222-2222-4222-8222-222222222203",
            reference_code=f"PR-{day}-0003",
            share_token="seed-share-paid-ogulcan-ayca",
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
            request_id="22222222-2222-4222-8222-222222222204",
            reference_code=f"PR-{day}-0004",
            share_token="seed-share-declined-mehmet-ogulcan",
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
            request_id="22222222-2222-4222-8222-222222222205",
            reference_code=f"PR-{day}-0005",
            share_token="seed-share-cancel-ogulcan-ayca",
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
            request_id="22222222-2222-4222-8222-222222222206",
            reference_code=f"PR-{day}-0006",
            share_token="seed-share-expired-ayca-ogulcan",
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
            request_id="22222222-2222-4222-8222-222222222207",
            reference_code=f"PR-{day}-0007",
            share_token="seed-share-phone-ogulcan-mehmet",
            sender=ogulcan,
            recipient_contact="+905551234567",
            recipient_user=mehmet,
            amount_minor=9900,
            status=PaymentRequestStatus.PENDING.value,
            note="Phone recipient sample",
        )
        _request(
            db,
            request_id="22222222-2222-4222-8222-222222222208",
            reference_code=f"PR-{day}-0008",
            share_token="seed-share-cancel-target",
            sender=ogulcan,
            recipient_contact="ayca@example.com",
            recipient_user=ayca,
            amount_minor=4200,
            status=PaymentRequestStatus.PENDING.value,
            note="E2E cancel target",
        )
        _request(
            db,
            request_id="22222222-2222-4222-8222-222222222209",
            reference_code=f"PR-{day}-0009",
            share_token="seed-share-insufficient-mehmet",
            sender=ogulcan,
            recipient_contact="mehmet@example.com",
            recipient_user=mehmet,
            amount_minor=500_000,
            status=PaymentRequestStatus.PENDING.value,
            note="E2E insufficient balance target",
        )

        db.commit()
        print("Seed complete (deterministic). Demo users (password: 1234):")
        print("  ogulcan@example.com, ayca@example.com, mehmet@example.com (+905551234567)")
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the P2P payment request database")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop all tables and recreate seed data from scratch",
    )
    args = parser.parse_args()
    seed(reset=args.reset)


if __name__ == "__main__":
    main()
