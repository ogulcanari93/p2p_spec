# Tasks: P2P Payment Requests

**Input**: Design documents from `specs/001-p2p-payment-request/`  
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [data-model.md](./data-model.md), [contracts/openapi.yaml](./contracts/openapi.yaml), [research.md](./research.md), [quickstart.md](./quickstart.md)

**Tests**: Included — spec FR-033 (Playwright E2E) and FR-034 (pytest backend invariants) require automated tests.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no incomplete dependencies)
- **[Story]**: US1–US5 maps to spec.md user stories

## Path Conventions

- **Backend**: `backend/app/`, `backend/tests/`, `backend/seed.py`
- **Frontend**: `frontend/src/`
- **E2E**: `e2e/`

## Prototype Auth (A1)

- Protected API routes use **`X-User-Email` header only** (no session cookie/JWT in prototype). Frontend `api/client.ts` sets header after login; document limitation in README.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Monorepo scaffolding and tooling

- [ ] T001 Create `backend/`, `frontend/`, `e2e/` directories per `specs/001-p2p-payment-request/plan.md`
- [ ] T002 Create `backend/requirements.txt` with FastAPI, SQLAlchemy, Pydantic, Uvicorn, pytest, httpx
- [ ] T003 [P] Initialize `frontend/package.json` with React, Vite, TypeScript, React Router
- [ ] T004 [P] Initialize `e2e/package.json` with `@playwright/test`
- [ ] T005 Create `backend/app/__init__.py` and package layout (`routers/`, `services/` with `__init__.py`)
- [ ] T006 [P] Create `frontend/vite.config.ts` with `/api` proxy to `http://localhost:8000`
- [ ] T007 [P] Create `frontend/tsconfig.json` and `frontend/index.html`
- [ ] T008 [P] Add root `.gitignore` entries for `backend/.venv`, `backend/data/`, `frontend/dist`, `e2e/test-results/`
- [ ] T009 Create `README.md` skeleton with product summary and Spec-Kit artifact links

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database, models, core services, auth — **blocks all user stories**

**⚠️ CRITICAL**: No user story work until this phase is complete

- [ ] T010 Create `backend/app/config.py` with `DATABASE_URL`, `STATIC_DIR`, `CORS_ORIGINS` from env
- [ ] T011 Create `backend/app/database.py` with SQLAlchemy engine, `SessionLocal`, `Base`, `get_db`, `init_db`
- [ ] T012 Create `backend/app/models.py` with all six tables, indexes, and CHECK constraints per `data-model.md`
- [ ] T013 Create `backend/app/schemas.py` with enums (`PaymentRequestStatus`, `RecipientContactType`, etc.) and shared DTOs
- [ ] T014 [P] Implement `backend/app/services/money.py` — `parse_amount_to_minor`, TRY decimal rules, currency validation
- [ ] T015 [P] Implement `backend/app/services/security.py` — SHA-256 hashing, `build_destination_snapshot`, contact type detection
- [ ] T016 [P] Implement `backend/app/services/events.py` — `record_event()` with safe metadata only
- [ ] T017 [P] *(Optional, G3)* Extend `backend/app/services/events.py` to accept request context and populate `ip_address_hash` / `user_agent_hash` when available
- [ ] T018 Implement `backend/app/auth.py` — `get_current_user` from **`X-User-Email` header only**; 401 on missing/unknown (prototype auth per A1)
- [ ] T019 Implement `backend/app/services/wallets.py` — `ensure_default_wallet`, `get_default_wallet`
- [ ] T020 Implement `backend/app/services/payment_destinations.py` — `ensure_default_destination`, `get_user_destinations`, ownership helpers
- [ ] T021 Implement `backend/app/services/expiration.py` — `expire_pending_for_user`, bulk expire query
- [ ] T022 Create `backend/app/services/payment_requests.py` module skeleton with status transition helpers
- [ ] T023 Create `backend/app/main.py` — FastAPI app, CORS, include routers, health route
- [ ] T024 [P] Create `backend/app/routers/auth.py` router stub mounted at `/api/auth`
- [ ] T025 [P] Create `backend/app/routers/wallets.py` router stub mounted at `/api/wallets`
- [ ] T026 Create `backend/app/routers/payment_requests.py` router stub mounted at `/api/requests`
- [ ] T027 Create `backend/seed.py` stub that calls `init_db` only
- [ ] T028 Create `backend/tests/conftest.py` with test DB session and httpx `TestClient` fixtures
- [ ] T029 [P] Create `backend/tests/test_money.py` for amount parsing edge cases
- [ ] T030 Create `frontend/src/api/client.ts` with base URL, **`X-User-Email`** header on authenticated calls, error parsing
- [ ] T031 Create `frontend/src/auth/AuthContext.tsx` with login state persisted to `localStorage`
- [ ] T032 Create `frontend/src/App.tsx` with React Router routes skeleton and auth guard
- [ ] T033 [P] Create `frontend/src/components/Layout.tsx` with nav links and responsive shell
- [ ] T034 [P] Create `frontend/src/styles/global.css` with mobile-first layout tokens
- [ ] T035 Create `frontend/src/main.tsx` entry mounting `App` with `AuthProvider`

**Checkpoint**: `uvicorn app.main:app` starts; empty DB initializes; frontend dev server loads

---

## Phase 3: User Story 1 — Sign In and Request Money (Priority: P1) 🎯 MVP

**Goal**: Mock email login with default wallet/destination; create Pending payment request with share link. Post-login navigation must not 404 (minimal dashboard shell **or** redirect to `/requests/new` until full dashboard in US2).

**Independent Test**: Log in → land on valid route (shell or create) → create request → share URL → Pending in outgoing list (API or minimal shell)

### Implementation for User Story 1

- [ ] T036 [US1] Implement `POST /api/auth/login` and `GET /api/auth/me` in `backend/app/routers/auth.py` calling wallet/destination ensure
- [ ] T037 [US1] Add login/register and create-request schemas in `backend/app/schemas.py` — include `note` **max_length=280** (U2)
- [ ] T038 [US1] Implement `create_payment_request()` in `backend/app/services/payment_requests.py` — destination validation, snapshot, 7-day `expires_at`, `REQUEST_CREATED` event; **set `recipient_user_id` when normalized email/phone hash matches an existing user, else leave null** (U1)
- [ ] T039 [US1] Implement `POST /api/requests` in `backend/app/routers/payment_requests.py` per `contracts/openapi.yaml`
- [ ] T040 [US1] Implement `GET /api/payment-destinations/me` in `backend/app/routers/wallets.py` (mount path per OpenAPI)
- [ ] T041 [P] [US1] Create `frontend/src/components/LoginForm.tsx` and `frontend/src/pages/LoginPage.tsx`
- [ ] T042 [P] [US1] Create `frontend/src/components/AmountDisplay.tsx` and `frontend/src/components/StatusBadge.tsx`
- [ ] T043 [P] [US1] Create `frontend/src/components/DestinationSelector.tsx` loading destinations from API
- [ ] T044 [US1] Create `frontend/src/components/CreateRequestForm.tsx` — amount, contact, destination validation; **enforce note ≤280 characters in UI** (U2)
- [ ] T045 [US1] Create `frontend/src/pages/CreateRequestPage.tsx` wiring form to `POST /api/requests` and showing share link on success
- [ ] T046 [US1] Wire `/login` and `/requests/new` routes and auth redirect in `frontend/src/App.tsx`
- [ ] T047 [US1] Add post-login navigation in `frontend/src/App.tsx` — redirect to minimal `DashboardPage.tsx` shell (placeholder lists OK) **or** `/requests/new`; **must not route to an undefined page** (I2)
- [ ] T048 [US1] Add minimal `GET /api/requests?direction=outgoing` in `backend/app/services/payment_requests.py` for MVP verification (full list in US2)

**Checkpoint**: User can log in without 404, create request, copy share link; API returns 403 for another user's `destination_id`

---

## Phase 4: User Story 2 — Manage Requests on Dashboard (Priority: P1)

**Goal**: Dashboard with wallet balance, incoming/outgoing lists, status filter, search, responsive table/cards, and **correct Pending-row action affordances** (handlers completed in US3/US4).

**Independent Test**: Seed or create mixed-status requests → filter and search → Pending rows show correct buttons (stubs OK); terminal rows View Details only

**Dependency (I1)**: US2 renders Pay / Decline / Cancel / View Details buttons. **Full Pay** wired in US3 (T065). **Full Decline/Cancel** wired in US4 (T078).

### Implementation for User Story 2

- [X] T049 [US2] Implement full `list_payment_requests()` in `backend/app/services/payment_requests.py` — direction, status, search; incoming match by **`email_hash` or `phone_hash`** and `recipient_user_id` (U3)
- [X] T050 [US2] Call `expire_pending_for_user()` before list response in `backend/app/routers/payment_requests.py`
- [X] T051 [US2] Implement `GET /api/requests` and `GET /api/wallets/me` response shaping with `can_pay`/`can_decline`/`can_cancel` flags in `backend/app/schemas.py`
- [X] T052 [P] [US2] Create `frontend/src/components/WalletSummary.tsx` and `frontend/src/pages/DashboardPage.tsx`
- [X] T053 [P] [US2] Create `frontend/src/components/SearchAndFilterBar.tsx` for status and search query params
- [X] T054 [P] [US2] Create `frontend/src/components/RequestTable.tsx` for desktop layout (D1)
- [X] T055 [P] [US2] Create `frontend/src/components/RequestCard.tsx` for mobile layout
- [X] T056 [US2] Create `frontend/src/components/EmptyState.tsx` and integrate into `frontend/src/pages/DashboardPage.tsx`
- [X] T057 [US2] Add responsive CSS in `frontend/src/styles/global.css` — table vs cards breakpoint
- [X] T058 [US2] Wire `/dashboard` route with protected guard in `frontend/src/App.tsx`
- [X] T059 [US2] In `RequestTable.tsx` and `RequestCard.tsx`, render Pending-row actions: **incoming** → Pay, Decline, View Details; **outgoing** → Cancel, View Details; wire to **safe stub handlers** (disabled/loading/no-op or navigate to detail) until US3/US4 connect APIs (I1)

**Checkpoint**: Dashboard shows wallet, filtered lists, correct **visible** action buttons by status; Pay/Decline/Cancel may be stubs

---

## Phase 5: User Story 3 — Pay an Incoming Request (Priority: P1)

**Goal**: Replace Pay stubs with real payment; atomic wallet credit; 2–3s loading UI; idempotent pay

**Independent Test**: Recipient pays → status PAID → sender wallet balance increases → second pay rejected; sender cannot pay own outgoing → 403 (U4)

### Tests for User Story 3

- [X] T060 [P] [US3] Add duplicate-pay and wallet-credit assertions in `backend/tests/test_payment_requests.py`
- [X] T061 [P] [US3] Add pytest: sender **cannot** `POST /api/requests/{id}/pay` on own outgoing request → **403** (or domain-equivalent) (U4)

### Implementation for User Story 3

- [X] T062 [US3] Implement `pay_payment_request()` in `backend/app/services/payment_requests.py` — recipient auth, reject sender self-pay, expiration check, `UPDATE WHERE PENDING`, wallet CREDIT, `wallet_transactions`, `REQUEST_PAID` in one transaction
- [X] T063 [US3] Implement `POST /api/requests/{id}/pay` in `backend/app/routers/payment_requests.py`
- [X] T064 [P] [US3] Create `frontend/src/components/LoadingButton.tsx` with 2–3s minimum disabled state
- [X] T065 [US3] Connect dashboard **Pay** stubs in `RequestTable.tsx` / `RequestCard.tsx` to `LoadingButton` + pay API (replaces US2 stub) (I1)

**Checkpoint**: Pay flow credits sender wallet once; duplicate pay and self-pay rejected

---

## Phase 6: User Story 4 — Decline, Cancel, and View Details (Priority: P2)

**Goal**: Replace Decline/Cancel stubs; detail with events; public share page without sensitive fields

**Independent Test**: Decline incoming + cancel outgoing → detail shows events; `/r/:token` safe summary only

### Tests for User Story 4

- [ ] T066 [P] [US4] Add terminal-state transition rejection tests in `backend/tests/test_payment_requests.py`
- [ ] T067 [P] [US4] Add wrong-destination `403` test for `POST /api/requests` in `backend/tests/test_payment_requests.py`

### Implementation for User Story 4

- [ ] T068 [US4] Implement `decline_payment_request()` and `cancel_payment_request()` in `backend/app/services/payment_requests.py`
- [ ] T069 [US4] Implement `POST /api/requests/{id}/decline` and `POST /api/requests/{id}/cancel` in `backend/app/routers/payment_requests.py`
- [ ] T070 [US4] Implement `get_payment_request_detail()` with events in `backend/app/services/payment_requests.py`
- [ ] T071 [US4] Implement `GET /api/requests/{id}` in `backend/app/routers/payment_requests.py`
- [ ] T072 [US4] Implement `get_public_share_view()` returning `PublicShareView` schema only in `backend/app/services/payment_requests.py`
- [ ] T073 [US4] Implement `GET /api/share/{share_token}` in `backend/app/routers/payment_requests.py`
- [ ] T074 [P] [US4] Create `frontend/src/components/ExpirationCountdown.tsx` for Pending requests
- [ ] T075 [US4] Create `frontend/src/pages/RequestDetailPage.tsx` with actions, events, share link, countdown
- [ ] T076 [P] [US4] Create `frontend/src/pages/ShareRequestPage.tsx` at route `/r/:shareToken`
- [ ] T077 [US4] Wire `/requests/:id` and `/r/:shareToken` in `frontend/src/App.tsx`
- [ ] T078 [US4] Connect dashboard **Decline/Cancel** stubs and detail-page actions to decline/cancel APIs (replaces US2 stubs) (I1)

**Checkpoint**: Decline, cancel, detail, and public share flows work; terminal requests hide action buttons

---

## Phase 7: User Story 5 — Automatic Expiration (Priority: P2)

**Goal**: Pending requests expire after 7 days on read/action; expired requests reject pay/decline/cancel

**Independent Test**: Seed request with `expires_at` in past → list shows EXPIRED → pay returns clear error

### Implementation for User Story 5

- [ ] T079 [US5] Integrate `expire_pending_for_user()` in `GET /api/requests/{id}` and all mutation handlers in `backend/app/routers/payment_requests.py`
- [ ] T080 [US5] Return `422` with clear message when pay/decline/cancel attempted on EXPIRED in `backend/app/services/payment_requests.py`
- [ ] T081 [US5] Ensure `ExpirationCountdown.tsx` reflects server `expires_at` on `frontend/src/pages/RequestDetailPage.tsx`

**Checkpoint**: Expired requests auto-update on access; mutations blocked with user-friendly errors

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Seed data, static deploy, full test suite, documentation

- [ ] T082 Implement full `backend/seed.py` — users ogulcan/ayca/mehmet; **at least one user with `phone` + `phone_hash`**; wallets, destinations; requests in all statuses including pre-expired PENDING; include phone-targeted incoming sample for tests (U3)
- [ ] T083 Update `backend/app/main.py` to serve `frontend/dist` static files and SPA fallback excluding `/api/*`
- [ ] T084 Complete `README.md` — product, stack, Spec-Kit workflow, security model, **`X-User-Email` prototype auth**, PostgreSQL note, local run, seed, Playwright videos path, Render/Railway deploy; **logging policy: application logs and audit events must not contain raw sensitive financial identifiers** — do not log full recipient contacts, wallet IDs on public paths, encrypted identifiers, or provider refs (G2); note services should avoid logging these fields (G2)
- [ ] T085 [P] Create `e2e/playwright.config.ts` with `video: 'on'`, `webServer`, and a **mobile viewport project** (e.g. iPhone-sized) (G1)
- [ ] T086 Implement `e2e/tests/payment-requests.spec.ts` — all 10 scenarios from `plan.md` **plus mobile viewport dashboard usability check** (G1)
- [ ] T087 Run `specs/001-p2p-payment-request/quickstart.md` commands and fix any gaps
- [ ] T088 [P] Add production build script notes in `README.md` — `npm run build` + `STATIC_DIR` uvicorn
- [ ] T089 Align HTTP **403 / 404 / 422** responses across routers with `contracts/openapi.yaml` — user-friendly `detail`, no stack traces or internal IDs leaked (U5)
- [ ] T090 *(Process, C1)* Before final submission: run `/speckit-constitution` or update `.specify/memory/constitution.md` if project principles should be enforceable gates

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)** → **Phase 2 (Foundational)** → **User Stories (3–7)** → **Phase 8 (Polish)**
- **US2** depends on minimal list from T048 (or seed); full dashboard after US1 create flow
- **US2 (I1)**: Renders all Pending action buttons (T059); **US3** completes Pay (T065); **US4** completes Decline/Cancel (T078)
- **US3** depends on US2 Pay stubs; can test pay via API before T065
- **US4** depends on US2 Decline/Cancel stubs; detail/share can follow APIs
- **US5** layers on expiration service from Phase 2; wire-up after mutations exist

### User Story Dependencies

| Story | Depends on | Can test independently with |
|-------|------------|-------------------------------|
| US1 | Phase 2 | API login + create; valid post-login route (T047) |
| US2 | Phase 2, US1 (create) or seed | Seed; verify action affordances (stubs OK) |
| US3 | US2 Pay stubs | Two users + API; completes Pay |
| US4 | US2 Decline/Cancel stubs | Seed + API; completes Decline/Cancel |
| US5 | US3–US4 mutations | Seed expired row |

### Parallel Opportunities

- **Phase 1**: T003, T004, T006, T007, T008 in parallel
- **Phase 2**: T014–T017, T024–T025, T029, T033–T034 in parallel after T012
- **US1**: T041–T043 in parallel
- **US2**: T052–T055 in parallel
- **US4**: T066–T067, T074, T076 in parallel
- **Polish**: T085, T088 in parallel

### Parallel Example: User Story 2

```bash
# Frontend components in parallel:
T052 WalletSummary + DashboardPage
T053 SearchAndFilterBar
T054 RequestTable
T055 RequestCard
# Then T059 action affordances (stubs)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 + Phase 2  
2. Complete Phase 3 (US1) including T047 post-login navigation  
3. **STOP and VALIDATE**: Login → valid landing → create request → share link  
4. Demo if ready  

### Incremental Delivery

1. Setup + Foundational → foundation ready  
2. US1 → MVP create flow + safe login redirect  
3. US2 → Dashboard with action affordances (stubs)  
4. US3 → Pay + wallet credit  
5. US4 → Decline, cancel, detail, share  
6. US5 → Expiration hardening  
7. Polish → seed (incl. phone), E2E (incl. mobile), README, deploy  

### Suggested MVP Scope

**User Story 1 only** (Phases 1–3) delivers core “request money” value; add **US2** before recipient-facing dashboard demo.

---

## Notes

- Every task includes a file path; adjust only if plan structure changes  
- Never use float for money — use `backend/app/services/money.py` only  
- Public share responses must use `PublicShareView` — never expose `wallet_id` or `encrypted_identifier`  
- Prototype auth: **`X-User-Email` only** (A1)  
- Commit after each phase checkpoint  
- Total tasks: **90** (T001–T090)
