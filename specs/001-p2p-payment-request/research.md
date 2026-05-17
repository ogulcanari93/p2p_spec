# Research: P2P Payment Requests

**Feature**: `001-p2p-payment-request`  
**Date**: 2026-05-17

All technical choices are specified by stakeholders; no open NEEDS CLARIFICATION items remain.

## Decision: Monorepo with FastAPI + React (Vite)

**Rationale**: Clear separation of UI and API while allowing single-service deploy (FastAPI serves `frontend/dist`). Matches Venmo-style request UX with REST simplicity for prototype.

**Alternatives considered**:
- Next.js full-stack — rejected; stakeholder mandated FastAPI backend ownership of business rules.
- Separate static CDN deploy — rejected for prototype simplicity; single PaaS service preferred.

## Decision: SQLite (prototype) → PostgreSQL (production)

**Rationale**: Zero-config local dev; SQLAlchemy abstracts migration path. README must warn against SQLite for multi-instance production.

**Alternatives considered**:
- PostgreSQL in Docker for dev — deferred; adds setup friction for classroom/demo use.

## Decision: Integer minor units + Python `Decimal`

**Rationale**: Eliminates floating-point rounding bugs (fintech requirement). TRY stored as kuruş (×100).

**Alternatives considered**:
- `NUMERIC` in DB — acceptable in PostgreSQL production; prototype uses INTEGER minor for simplicity.

## Decision: Mock auth via `X-User-Email` header

**Rationale**: Fastest path for multi-user E2E (switch users by header). Session cookie optional enhancement; header sufficient for prototype.

**Alternatives considered**:
- JWT — out of scope; documented limitation.
- Cookie session — viable add-on; header chosen for Playwright test simplicity.

## Decision: On-read expiration (no cron in prototype)

**Rationale**: Meets FR-022 without worker infrastructure; idempotent expire updates safe to run on each list/detail/action.

**Alternatives considered**:
- APScheduler / Celery beat — production recommendation only; not needed for MVP.

## Decision: Destination snapshot JSON at create time

**Rationale**: Public share and historical UI show safe labels even if destination later changes; snapshot excludes wallet_id, encrypted fields, provider refs.

**Alternatives considered**:
- Live join only — fails share-page safety and audit consistency.

## Decision: Optimistic locking on pay via `UPDATE ... WHERE status='PENDING'`

**Rationale**: Prevents duplicate credits under concurrent pay without distributed locks; SQLite transaction serializes writes.

**Alternatives considered**:
- Idempotency-Key header — optional production enhancement; status guard sufficient for prototype.

## Decision: Playwright E2E with video recording

**Rationale**: Stakeholder requirement for demo/debug of fintech flows; `video: 'on'` in config.

**Alternatives considered**:
- Cypress — not specified; Playwright mandated.

## Decision: Contact hashing (SHA-256) for lookup

**Rationale**: Supports incoming request matching by email/phone hash without storing reversible secrets in indexes; aligns with FR-026 (no raw sensitive data in logs).

**Alternatives considered**:
- Plaintext index only — weaker privacy; hash + plaintext contact field for display still required on request row.

## Decision: Single TRY currency default

**Rationale**: Spec default TRY with 2 decimal validation; schema uses 3-letter ISO codes for future expansion.

**Alternatives considered**:
- Multi-currency wallets day one — out of scope except schema readiness.
