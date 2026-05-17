def _headers(email: str) -> dict[str, str]:
    return {"X-User-Email": email}


def _login(client, email: str, password: str = "1234") -> None:
    assert (
        client.post("/api/auth/login", json={"email": email, "password": password}).status_code
        == 200
    )


def test_login_rejects_wrong_password(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "alice@example.com", "password": "wrong"},
    )
    assert response.status_code == 401
    assert "invalid email or password" in response.json()["detail"].lower()


def test_login_rejects_unknown_user(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "1234"},
    )
    assert response.status_code == 401


def test_note_max_length_rejected(client):
    _login(client, "alice@example.com")
    response = client.post(
        "/api/requests",
        json={
            "recipient_contact": "bob@example.com",
            "amount": "10.00",
            "note": "x" * 281,
        },
        headers=_headers("alice@example.com"),
    )
    assert response.status_code == 422
    assert "280" in response.json()["detail"]


def test_unhandled_errors_do_not_leak_internals(db_session, monkeypatch):
    from app.database import get_db
    from app.main import app
    from fastapi.testclient import TestClient

    def boom(*_args, **_kwargs):
        raise RuntimeError("secret-sql-detail-uuid-12345")

    monkeypatch.setattr("app.routers.payment_requests.list_payment_requests", boom)
    monkeypatch.setattr("app.main.init_db", lambda: None)

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            _login(client, "alice@example.com")
            response = client.get("/api/requests", headers=_headers("alice@example.com"))
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 500
    body = response.json()
    assert "secret-sql" not in body["detail"].lower()
    assert "uuid" not in body["detail"].lower()
