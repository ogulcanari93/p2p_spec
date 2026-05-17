from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.models import PaymentRequest, PaymentRequestStatus, RequestEvent, RequestEventType, WalletTransaction


def _headers(email: str) -> dict[str, str]:
    return {"X-User-Email": email}


def _login(client, email: str, password: str = "1234") -> None:
    assert (
        client.post("/api/auth/login", json={"email": email, "password": password}).status_code
        == 200
    )


def _create_request(client, sender: str, recipient: str) -> str:
    _login(client, sender)
    if "@" in recipient:
        _login(client, recipient.strip().lower())

    res = client.post(
        "/api/requests",
        json={"recipient_contact": recipient, "amount": "50.00", "currency": "TRY"},
        headers=_headers(sender),
    )
    assert res.status_code == 201
    return res.json()["request"]["id"]


def test_created_request_expires_in_seven_days(client, db_session):
    _login(client, "alice@example.com")
    request_id = _create_request(client, "alice@example.com", "bob@example.com")
    request = db_session.get(PaymentRequest, request_id)
    assert request is not None
    delta = request.expires_at - request.created_at
    assert timedelta(days=6, hours=23) <= delta <= timedelta(days=7, hours=1)


def test_pending_past_expiry_becomes_expired_on_list_with_event(client, db_session):
    _login(client, "alice@example.com")
    _login(client, "bob@example.com")

    request_id = _create_request(client, "alice@example.com", "bob@example.com")
    request = db_session.get(PaymentRequest, request_id)
    request.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db_session.commit()

    response = client.get("/api/requests", headers=_headers("bob@example.com"))
    assert response.status_code == 200
    incoming = next((r for r in response.json()["incoming"] if r["id"] == request_id), None)
    assert incoming is not None
    assert incoming["status"] == "EXPIRED"

    db_session.expire_all()
    stored = db_session.get(PaymentRequest, request_id)
    assert stored.status == PaymentRequestStatus.EXPIRED.value
    assert stored.expired_at is not None

    events = db_session.execute(
        select(RequestEvent).where(RequestEvent.payment_request_id == request_id)
    ).scalars().all()
    assert any(e.event_type == RequestEventType.REQUEST_EXPIRED.value for e in events)


def test_share_endpoint_expires_due_request(client, db_session):
    _login(client, "alice@example.com")
    _login(client, "bob@example.com")
    create = client.post(
        "/api/requests",
        json={"recipient_contact": "bob@example.com", "amount": "10.00"},
        headers=_headers("alice@example.com"),
    )
    share_token = create.json()["request"]["share_token"]
    request = db_session.execute(
        select(PaymentRequest).where(PaymentRequest.share_token == share_token)
    ).scalar_one()
    request.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
    db_session.commit()

    share = client.get(f"/api/share/{share_token}")
    assert share.status_code == 200
    assert share.json()["status"] == "EXPIRED"


def test_expired_request_cannot_be_declined_or_cancelled(client, db_session):
    _login(client, "alice@example.com")
    _login(client, "bob@example.com")

    request_id = _create_request(client, "alice@example.com", "bob@example.com")
    request = db_session.get(PaymentRequest, request_id)
    request.status = PaymentRequestStatus.EXPIRED.value
    request.expired_at = datetime.now(timezone.utc)
    db_session.commit()

    decline = client.post(f"/api/requests/{request_id}/decline", headers=_headers("bob@example.com"))
    assert decline.status_code == 422
    assert "expired" in decline.json()["detail"].lower()

    cancel = client.post(f"/api/requests/{request_id}/cancel", headers=_headers("alice@example.com"))
    assert cancel.status_code == 422
    assert "expired" in cancel.json()["detail"].lower()


def test_expired_pay_does_not_credit_wallet(client, db_session):
    _login(client, "alice@example.com")
    _login(client, "bob@example.com")

    request_id = _create_request(client, "alice@example.com", "bob@example.com")
    request = db_session.get(PaymentRequest, request_id)
    request.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
    db_session.commit()

    wallet_before = client.get("/api/wallets/me", headers=_headers("alice@example.com")).json()[
        "balance_minor"
    ]

    pay = client.post(f"/api/requests/{request_id}/pay", headers=_headers("bob@example.com"))
    assert pay.status_code == 422

    wallet_after = client.get("/api/wallets/me", headers=_headers("alice@example.com")).json()[
        "balance_minor"
    ]
    assert wallet_after == wallet_before

    credits = db_session.execute(
        select(WalletTransaction).where(WalletTransaction.payment_request_id == request_id)
    ).scalars().all()
    assert len(credits) == 0


def test_terminal_paid_request_not_changed_by_expiration(client, db_session):
    _login(client, "alice@example.com")
    _login(client, "bob@example.com")

    request_id = _create_request(client, "alice@example.com", "bob@example.com")
    request = db_session.get(PaymentRequest, request_id)
    request.status = PaymentRequestStatus.PAID.value
    request.paid_at = datetime.now(timezone.utc)
    request.expires_at = datetime.now(timezone.utc) - timedelta(days=10)
    db_session.commit()

    client.get("/api/requests", headers=_headers("alice@example.com"))

    db_session.expire_all()
    stored = db_session.get(PaymentRequest, request_id)
    assert stored.status == PaymentRequestStatus.PAID.value
    events = db_session.execute(
        select(RequestEvent).where(
            RequestEvent.payment_request_id == request_id,
            RequestEvent.event_type == RequestEventType.REQUEST_EXPIRED.value,
        )
    ).scalars().all()
    assert len(events) == 0
