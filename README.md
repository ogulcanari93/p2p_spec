# P2P Payment Requests

Consumer fintech prototype for requesting money from friends (similar to Venmo Request). Users log in with email, create payment requests to a payout destination they own, and share a link with recipients.

## Spec-Kit artifacts

| Artifact | Path |
|----------|------|
| Specification | [specs/001-p2p-payment-request/spec.md](specs/001-p2p-payment-request/spec.md) |
| Plan | [specs/001-p2p-payment-request/plan.md](specs/001-p2p-payment-request/plan.md) |
| Tasks | [specs/001-p2p-payment-request/tasks.md](specs/001-p2p-payment-request/tasks.md) |

## Tech stack

- **Frontend**: React, Vite, TypeScript
- **Backend**: Python, FastAPI, SQLAlchemy
- **Database**: SQLite (prototype; use PostgreSQL in production)

## Prototype authentication

Protected API routes use the **`X-User-Email` header** only (no JWT/session). This is **not production-safe**.

## Security & logging

- Public share responses expose only `PublicShareView` fields (no `wallet_id`, `destination_id`, `encrypted_identifier`, or provider refs).
- Application logs and audit event metadata must not include raw recipient contacts, wallet IDs on public paths, encrypted identifiers, or provider account references.

## Local development

See [specs/001-p2p-payment-request/quickstart.md](specs/001-p2p-payment-request/quickstart.md) for full commands.

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python seed.py
uvicorn app.main:app --reload --port 8000
```

### Frontend (dev with API proxy)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

### Production-style (single server)

```bash
cd frontend && npm run build
cd ../backend && source .venv/bin/activate
export STATIC_DIR=../frontend/dist
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000

### Demo seed users

After `python seed.py`:

| Email | Notes |
|-------|--------|
| `ogulcan@example.com` | Sender with mixed outgoing requests |
| `ayca@example.com` | Recipient / sender samples |
| `mehmet@example.com` | Has phone `+905551234567` for phone-match incoming |

### Tests

```bash
cd backend
source .venv/bin/activate
pytest -v
```

Tests use an isolated in-memory SQLite database (`tests/conftest.py`) and do not require `data/app.db`.

## Playwright E2E

Planned under `e2e/` (see tasks T085–T086). Run with video on failure when configured.
