from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.models import (
    PaymentRequest,
    PaymentRequestStatus,
    RequestEvent,
    RequestEventType,
    WalletTransaction,
    WalletTransactionDirection,
)


def _headers(email: str) -> dict[str, str]:
    return {"X-User-Email": email}


def _login(client, email: str) -> None:
    response = client.post("/api/auth/login", json={"email": email})
    assert response.status_code == 200


def _create_request(
    client,
    sender_email: str,
    recipient: str,
    amount: str = "100.00",
    destination_id: str | None = None,
) -> str:
    payload: dict = {
        "recipient_contact": recipient,
        "amount": amount,
        "currency": "TRY",
    }
    if destination_id:
        payload["destination_id"] = destination_id
    response = client.post(
        "/api/requests",
        json=payload,
        headers=_headers(sender_email),
    )
    assert response.status_code == 201
    return response.json()["request"]["id"]


def _wallet_balance(client, email: str) -> int:
    response = client.get("/api/wallets/me", headers=_headers(email))
    assert response.status_code == 200
    return response.json()["balance_minor"]


def test_recipient_can_pay_pending_request(client):
    _login(client, "alice@example.com")
    _login(client, "bob@example.com")

    request_id = _create_request(client, "alice@example.com", "bob@example.com")
    balance_before = _wallet_balance(client, "alice@example.com")

    pay_response = client.post(f"/api/requests/{request_id}/pay", headers=_headers("bob@example.com"))
    assert pay_response.status_code == 200
    body = pay_response.json()
    assert body["status"] == "PAID"
    assert body["paid_at"] is not None
    assert body["can_pay"] is False

    balance_after = _wallet_balance(client, "alice@example.com")
    assert balance_after == balance_before + 10000


def test_sender_cannot_pay_own_outgoing_request(client):
    _login(client, "alice@example.com")
    request_id = _create_request(client, "alice@example.com", "bob@example.com")

    response = client.post(f"/api/requests/{request_id}/pay", headers=_headers("alice@example.com"))
    assert response.status_code == 403
    assert "cannot pay your own" in response.json()["detail"].lower()


def test_duplicate_pay_does_not_duplicate_wallet_credit(client, db_session):
    _login(client, "alice@example.com")
    _login(client, "bob@example.com")

    request_id = _create_request(client, "alice@example.com", "bob@example.com")
    balance_before = _wallet_balance(client, "alice@example.com")

    first = client.post(f"/api/requests/{request_id}/pay", headers=_headers("bob@example.com"))
    assert first.status_code == 200

    balance_after_first = _wallet_balance(client, "alice@example.com")
    assert balance_after_first == balance_before + 10000

    second = client.post(f"/api/requests/{request_id}/pay", headers=_headers("bob@example.com"))
    assert second.status_code == 409

    balance_after_second = _wallet_balance(client, "alice@example.com")
    assert balance_after_second == balance_after_first

    credits = db_session.execute(
        select(WalletTransaction).where(
            WalletTransaction.payment_request_id == request_id,
            WalletTransaction.direction == WalletTransactionDirection.CREDIT.value,
        )
    ).scalars().all()
    assert len(credits) == 1


def test_terminal_request_cannot_be_paid(client, db_session):
    _login(client, "alice@example.com")
    _login(client, "bob@example.com")

    request_id = _create_request(client, "alice@example.com", "bob@example.com")
    request = db_session.get(PaymentRequest, request_id)
    request.status = PaymentRequestStatus.DECLINED.value
    db_session.commit()

    response = client.post(f"/api/requests/{request_id}/pay", headers=_headers("bob@example.com"))
    assert response.status_code == 422
    assert "cannot pay" in response.json()["detail"].lower()


def test_expired_request_cannot_be_paid(client, db_session):
    _login(client, "alice@example.com")
    _login(client, "bob@example.com")

    request_id = _create_request(client, "alice@example.com", "bob@example.com")
    request = db_session.get(PaymentRequest, request_id)
    request.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    db_session.commit()

    response = client.post(f"/api/requests/{request_id}/pay", headers=_headers("bob@example.com"))
    assert response.status_code == 422
    assert "expired" in response.json()["detail"].lower()


def test_recipient_can_decline_pending_request(client, db_session):
    _login(client, "alice@example.com")
    _login(client, "bob@example.com")

    request_id = _create_request(client, "alice@example.com", "bob@example.com")
    response = client.post(
        f"/api/requests/{request_id}/decline",
        headers=_headers("bob@example.com"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "DECLINED"
    assert body["declined_at"] is not None
    assert body["can_decline"] is False

    events = db_session.execute(
        select(RequestEvent).where(RequestEvent.payment_request_id == request_id)
    ).scalars().all()
    assert any(e.event_type == RequestEventType.REQUEST_DECLINED.value for e in events)


def test_sender_can_cancel_pending_outgoing_request(client, db_session):
    _login(client, "alice@example.com")
    _login(client, "bob@example.com")

    request_id = _create_request(client, "alice@example.com", "bob@example.com")
    response = client.post(
        f"/api/requests/{request_id}/cancel",
        headers=_headers("alice@example.com"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "CANCELLED"
    assert body["cancelled_at"] is not None
    assert body["can_cancel"] is False

    events = db_session.execute(
        select(RequestEvent).where(RequestEvent.payment_request_id == request_id)
    ).scalars().all()
    assert any(e.event_type == RequestEventType.REQUEST_CANCELLED.value for e in events)


def test_non_recipient_cannot_decline(client):
    _login(client, "alice@example.com")
    _login(client, "bob@example.com")
    _login(client, "carol@example.com")

    request_id = _create_request(client, "alice@example.com", "bob@example.com")
    response = client.post(
        f"/api/requests/{request_id}/decline",
        headers=_headers("carol@example.com"),
    )
    assert response.status_code == 403


def test_non_sender_cannot_cancel(client):
    _login(client, "alice@example.com")
    _login(client, "bob@example.com")

    request_id = _create_request(client, "alice@example.com", "bob@example.com")
    response = client.post(
        f"/api/requests/{request_id}/cancel",
        headers=_headers("bob@example.com"),
    )
    assert response.status_code == 403


def test_terminal_request_cannot_be_declined(client, db_session):
    _login(client, "alice@example.com")
    _login(client, "bob@example.com")

    request_id = _create_request(client, "alice@example.com", "bob@example.com")
    request = db_session.get(PaymentRequest, request_id)
    request.status = PaymentRequestStatus.PAID.value
    db_session.commit()

    response = client.post(
        f"/api/requests/{request_id}/decline",
        headers=_headers("bob@example.com"),
    )
    assert response.status_code == 422


def test_terminal_request_cannot_be_cancelled(client, db_session):
    _login(client, "alice@example.com")
    _login(client, "bob@example.com")

    request_id = _create_request(client, "alice@example.com", "bob@example.com")
    request = db_session.get(PaymentRequest, request_id)
    request.status = PaymentRequestStatus.PAID.value
    db_session.commit()

    response = client.post(
        f"/api/requests/{request_id}/cancel",
        headers=_headers("alice@example.com"),
    )
    assert response.status_code == 422


def test_expired_request_cannot_be_declined(client, db_session):
    _login(client, "alice@example.com")
    _login(client, "bob@example.com")

    request_id = _create_request(client, "alice@example.com", "bob@example.com")
    request = db_session.get(PaymentRequest, request_id)
    request.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    db_session.commit()

    response = client.post(
        f"/api/requests/{request_id}/decline",
        headers=_headers("bob@example.com"),
    )
    assert response.status_code == 422
    assert "expired" in response.json()["detail"].lower()


def test_expired_request_cannot_be_cancelled(client, db_session):
    _login(client, "alice@example.com")
    _login(client, "bob@example.com")

    request_id = _create_request(client, "alice@example.com", "bob@example.com")
    request = db_session.get(PaymentRequest, request_id)
    request.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    db_session.commit()

    response = client.post(
        f"/api/requests/{request_id}/cancel",
        headers=_headers("alice@example.com"),
    )
    assert response.status_code == 422
    assert "expired" in response.json()["detail"].lower()


def test_get_request_detail_includes_events(client):
    _login(client, "alice@example.com")
    _login(client, "bob@example.com")

    request_id = _create_request(client, "alice@example.com", "bob@example.com")
    response = client.get(f"/api/requests/{request_id}", headers=_headers("bob@example.com"))
    assert response.status_code == 200
    body = response.json()
    assert body["sender"]["email"] == "alice@example.com"
    assert len(body["events"]) >= 1
    assert body["events"][0]["event_type"] == RequestEventType.REQUEST_CREATED.value


def test_create_request_with_another_users_destination_returns_403(client):
    _login(client, "alice@example.com")
    _login(client, "bob@example.com")

    destinations = client.get(
        "/api/payment-destinations/me",
        headers=_headers("alice@example.com"),
    )
    assert destinations.status_code == 200
    alice_destination_id = destinations.json()[0]["id"]

    response = client.post(
        "/api/requests",
        json={
            "recipient_contact": "carol@example.com",
            "amount": "50.00",
            "currency": "TRY",
            "destination_id": alice_destination_id,
        },
        headers=_headers("bob@example.com"),
    )
    assert response.status_code == 403


def test_expired_status_cannot_be_paid(client, db_session):
    _login(client, "alice@example.com")
    _login(client, "bob@example.com")

    request_id = _create_request(client, "alice@example.com", "bob@example.com")
    request = db_session.get(PaymentRequest, request_id)
    request.status = PaymentRequestStatus.EXPIRED.value
    request.expired_at = datetime.now(timezone.utc)
    db_session.commit()

    response = client.post(f"/api/requests/{request_id}/pay", headers=_headers("bob@example.com"))
    assert response.status_code == 422
    assert "expired" in response.json()["detail"].lower()


def test_list_expires_pending_requests(client, db_session):
    _login(client, "alice@example.com")

    request_id = _create_request(client, "alice@example.com", "bob@example.com")
    request = db_session.get(PaymentRequest, request_id)
    request.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
    db_session.commit()

    response = client.get("/api/requests", headers=_headers("alice@example.com"))
    assert response.status_code == 200
    outgoing = response.json()["outgoing"]
    match = next((r for r in outgoing if r["id"] == request_id), None)
    assert match is not None
    assert match["status"] == "EXPIRED"


def test_public_share_excludes_sensitive_fields(client):
    _login(client, "alice@example.com")
    create_response = client.post(
        "/api/requests",
        json={"recipient_contact": "bob@example.com", "amount": "25.00", "currency": "TRY"},
        headers=_headers("alice@example.com"),
    )
    share_token = create_response.json()["request"]["share_token"]

    response = client.get(f"/api/share/{share_token}")
    assert response.status_code == 200
    body = response.json()
    forbidden_keys = {
        "destination_id",
        "wallet_id",
        "encrypted_identifier",
        "provider_account_ref",
        "provider_name",
        "destination_snapshot",
        "recipient_contact",
    }
    for key in forbidden_keys:
        assert key not in body
    assert "sender_display" in body
    assert "recipient_contact_masked" in body
