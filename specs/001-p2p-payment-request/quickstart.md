# Quickstart: P2P Payment Requests

**Feature**: `001-p2p-payment-request`  
**Branch**: `001-p2p-payment-request`

## Prerequisites

- Python 3.11+
- Node.js 20+
- npm or pnpm

## Initial Setup

```bash
# From repository root
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cd ../frontend
npm install

cd ../e2e
npm install
npx playwright install
```

## Database & Seed

```bash
cd backend
source .venv/bin/activate
python seed.py
```

Creates SQLite DB (default `backend/data/app.db`), three seed users, wallets, destinations, and sample requests.

**Seed logins**: `ogulcan@example.com`, `ayca@example.com`, `mehmet@example.com`

## Local Development (two terminals)

**Terminal 1 — API**:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend** (proxies `/api` → `localhost:8000`):

```bash
cd frontend
npm run dev
```

Open http://localhost:5173 (or Vite default port).

### Auth in dev

After login, API client sends header:

```http
X-User-Email: user@example.com
```

## Production Build (local smoke test)

```bash
cd frontend && npm run build
cd ../backend
source .venv/bin/activate
export STATIC_DIR=../frontend/dist
uvicorn app.main:app --port 8000
```

Open http://localhost:8000 — API and SPA served from one process.

## Backend Tests

```bash
cd backend
source .venv/bin/activate
pytest -q
```

## E2E Tests (Playwright)

```bash
# Ensure API + seed running, or use webServer in playwright.config
cd e2e
npm test
```

**Videos**: saved under `e2e/test-results/` (per Playwright config `video: 'on'`).

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | `sqlite:///./data/app.db` | SQLAlchemy URL |
| `STATIC_DIR` | `../frontend/dist` | React build for FastAPI |
| `CORS_ORIGINS` | `http://localhost:5173` | Dev CORS |

## Deployment (Render / Railway)

1. Build command: `cd frontend && npm ci && npm run build && cd ../backend && pip install -r requirements.txt`
2. Start command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Set `STATIC_DIR` to absolute path of `frontend/dist`
4. Run `python seed.py` once via release command or manual shell
5. **Production DB**: Replace SQLite with PostgreSQL `DATABASE_URL` before real launch (see README)

## Spec-Kit Artifacts

| Artifact | Path |
|----------|------|
| Specification | `specs/001-p2p-payment-request/spec.md` |
| Plan | `specs/001-p2p-payment-request/plan.md` |
| Data model | `specs/001-p2p-payment-request/data-model.md` |
| API contract | `specs/001-p2p-payment-request/contracts/openapi.yaml` |
| Tasks (after `/speckit-tasks`) | `specs/001-p2p-payment-request/tasks.md` |

## Next Steps

Run `/speckit-tasks` then `/speckit-implement` to build the application per plan.
