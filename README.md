# P2P Payment Requests

A consumer fintech prototype for requesting money from friends—similar to **Venmo Request** or **Cash App Request**. Senders create a payment request tied to their payout destination; recipients pay or decline from a dashboard or from a public share link.

**Repository:** https://github.com/ogulcanari93/p2p_spec

| | |
|---|---|
| **Live demo** | https://p2p-payment-request.onrender.com/login |
| **Demo video** | [docs/demo/walkthrough.webm](docs/demo/walkthrough.webm) (automated Playwright tour, ~2 min) |

### Quick try (no install)

Open the [live demo](https://p2p-payment-request.onrender.com/login) and sign in as `ayca@example.com` with password `1234`. Pay a pending incoming request, then sign in as `ogulcan@example.com` / `1234` to confirm it shows **Paid**. All seed users use password `1234`.

> Free tier may cold-start after idle time (~30–60 s on first load).

---

## What is in this repo

Everything required for review is included in one place:

| Deliverable | Location |
|-------------|----------|
| **Spec-Kit specification** | [specs/001-p2p-payment-request/spec.md](specs/001-p2p-payment-request/spec.md) |
| **Implementation plan** | [specs/001-p2p-payment-request/plan.md](specs/001-p2p-payment-request/plan.md) |
| **Research & data model** | [research.md](specs/001-p2p-payment-request/research.md), [data-model.md](specs/001-p2p-payment-request/data-model.md) |
| **OpenAPI contract** | [contracts/openapi.yaml](specs/001-p2p-payment-request/contracts/openapi.yaml) |
| **Task breakdown** | [tasks.md](specs/001-p2p-payment-request/tasks.md) |
| **Spec-Kit tooling** | [.specify/](.specify/), [.cursor/skills/](.cursor/skills/) |
| **Backend source** | [backend/](backend/) |
| **Frontend source** | [frontend/](frontend/) |
| **E2E test suite** | [e2e/](e2e/) |
| **Screen recording** | [docs/demo/walkthrough.webm](docs/demo/walkthrough.webm) |
| **Deploy config** | [render.yaml](render.yaml) |

---

## Features

- Email + password sign-in (prototype; seed users below)
- Dashboard with wallet balance, incoming/outgoing requests, status filter, and search
- Create request to a **registered** recipient (email or phone)
- Human-readable **Request ID** (`PR-YYYYMMDD-NNNN`) on create, detail, share page, and success modals
- Pay / Decline / Cancel with loading overlay and in-app success/error modals
- Insufficient balance check before pay
- Public share link (`/r/:token`) with masked fields only
- Lifecycle: Pending → Paid / Declined / Cancelled / Expired (7-day expiration on read/action)

---

## Tech stack

| Layer | Stack |
|-------|--------|
| Frontend | React 18, Vite 5, TypeScript, React Router |
| Backend | Python 3.12+, FastAPI, SQLAlchemy 2, Pydantic v2 |
| Database | SQLite (prototype) |
| Tests | pytest, Playwright |

### AI tools used

- **[GitHub Spec Kit](https://github.com/github/spec-kit)** — `/speckit.specify`, `/speckit.plan`, `/speckit.tasks`, `/speckit.implement`
- **[Cursor](https://cursor.com)** — implementation, tests, UX polish, documentation

Spec Kit drove the spec → plan → tasks → incremental delivery workflow. Cursor was used for coding and review; behavior was validated with automated tests.

---

## Local setup

**Prerequisites:** Python 3.12+, Node.js 18+

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python seed.py --reset
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend (second terminal)

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** (API proxied to port 8000).

### Demo accounts (password `1234` for all)

| Email | Notes |
|-------|--------|
| `ogulcan@example.com` | Sender / mixed sample requests |
| `ayca@example.com` | Recipient; wallet ~5000 TRY |
| `mehmet@example.com` | Phone `+905551234567`; use for insufficient-balance demo |

---

## Tests

### Backend (pytest)

```bash
cd backend && source .venv/bin/activate && pytest -v
```

### E2E (Playwright)

```bash
cd e2e
npm install
npx playwright install chromium
npm run test
```

Uses ports **8001** (API) and **5174** (UI). Covers happy paths, edge cases (wrong password, unknown recipient, self-request, insufficient balance, share-link pay), and mobile dashboard.

### Re-record demo video

```bash
./scripts/record-demo.sh
```

Writes to `docs/demo/walkthrough.webm`.

---

## Live demo

**URL:** https://p2p-payment-request.onrender.com/login

Hosted on [Render](https://render.com) via [render.yaml](render.yaml). Each deploy re-seeds demo data. To redeploy or change hosting, see [docs/DEPLOY.md](docs/DEPLOY.md).

---

## Spec-Kit workflow

1. **Specify** — user stories, FRs, edge cases → `spec.md`
2. **Plan** — architecture, contracts → `plan.md`, `openapi.yaml`
3. **Tasks** — ordered implementation → `tasks.md`
4. **Implement** — backend, frontend, seed, E2E, polish

---

## Security notes (prototype)

- After login, the API trusts `X-User-Email` (no JWT). Documented as non-production.
- Amounts stored as integer minor units; TRY validated to two decimal places.
- Public share responses exclude wallet IDs and sensitive destination data.

---

## License

MIT — see [LICENSE](LICENSE) if present.
