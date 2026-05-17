# Deploy live demo (Render)

Use this **before** or right after pushing to [ogulcanari93/p2p_spec](https://github.com/ogulcanari93/p2p_spec.git). The app runs as a **single web service**: FastAPI serves the React build and `/api/*`.

## Prerequisites

- GitHub repo pushed (public)
- [Render](https://render.com) account (free tier is enough)

## Steps

1. Open [Render Dashboard](https://dashboard.render.com/) → **New** → **Blueprint**.
2. Connect GitHub and select repository **`ogulcanari93/p2p_spec`**.
3. Render detects `render.yaml` at the repo root. Confirm and **Apply**.
4. Wait for the first deploy (build frontend → install Python deps → seed → start uvicorn).
5. Copy the service URL (e.g. `https://p2p-payment-request.onrender.com`).
6. Update the **Live demo** line at the top of root `README.md` with that URL.
7. Open `/health` — should return `{"status":"ok"}`.
8. Open `/` — login with seed user + password `1234` (see README).

### Cold starts (free tier)

Free services sleep after ~15 minutes of inactivity. The first request after sleep may take **30–60 seconds**. Demo data is re-seeded on **every deploy** (`python seed.py --reset` in `startCommand`).

## Environment variables (optional)

| Variable | When to set |
|----------|-------------|
| `APP_BASE_URL` | Only if auto-detection fails; normally `RENDER_EXTERNAL_URL` is enough |
| `CORS_ORIGINS` | Extra origins beyond the Render URL |
| `DATABASE_URL` | Use PostgreSQL in production; SQLite is prototype-only |

## Verify without local setup

1. Open live URL in a browser.
2. Log in as `ayca@example.com` / `1234`.
3. Open an incoming **Pending** request → **Pay** → success modal.
4. Log in as `ogulcan@example.com` / `1234` → confirm **Paid** on dashboard.

## Railway (alternative)

Same commands as `render.yaml`:

- **Build:** `cd frontend && npm ci && npm run build && cd ../backend && pip install -r requirements.txt`
- **Start:** `cd backend && mkdir -p data && python seed.py --reset && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Set `STATIC_DIR=../frontend/dist`, `DATABASE_URL=sqlite:///./data/app.db`
- `config.py` reads `RAILWAY_PUBLIC_DOMAIN` for share links and CORS.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| 502 on first visit | Wait for cold start; check Render logs |
| Blank page | Build failed — confirm `frontend/dist` exists in build logs |
| API 404 | Ensure you are not mounting only `/api` on a separate host; use single-service mode |
| Share links wrong | Set `APP_BASE_URL` to your public HTTPS URL |
