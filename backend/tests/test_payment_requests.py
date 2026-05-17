from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.models import PaymentRequest, PaymentRequestStatus, WalletTransaction, WalletTransactionDirection


def _headers(email: str) -> dict[str, str]:
    return {"X-User-Email": email}


def _login(client, email: str) -> None:
    response = client.post("/api/auth/login", json={"email": email})
    assert response.status_code == 200


def _create_request(client, sender_email: str, recipient: str, amount: str = "100.00") -> str:
    response = client.post(
        "/api/requests",
        json={"recipient_contact": recipient, "amount": amount, "currency": "TRY"},
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
