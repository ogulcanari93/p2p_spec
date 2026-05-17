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

## Local development

See [specs/001-p2p-payment-request/quickstart.md](specs/001-p2p-payment-request/quickstart.md) for full commands.

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

### Database init

```bash
cd backend
source .venv/bin/activate
python seed.py
```

Full demo seed data is planned in a later implementation phase.
