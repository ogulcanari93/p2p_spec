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
- [ ] T017 Implement `backend/app/auth.py` — `get_current_user` from `X-User-Email`, 401 on missing/unknown
- [ ] T018 Implement `backend/app/services/wallets.py` — `ensure_default_wallet`, `get_default_wallet`
- [ ] T019 Implement `backend/app/services/payment_destinations.py` — `ensure_default_destination`, `get_user_destinations`, ownership helpers
- [ ] T020 Implement `backend/app/services/expiration.py` — `expire_pending_for_user`, bulk expire query
- [ ] T021 Create `backend/app/services/payment_requests.py` module skeleton with status transition helpers
- [ ] T022 Create `backend/app/main.py` — FastAPI app, CORS, include routers, health route
- [ ] T023 [P] Create `backend/app/routers/auth.py` router stub mounted at `/api/auth`
- [ ] T024 [P] Create `backend/app/routers/wallets.py` router stub mounted at `/api/wallets`
- [ ] T025 Create `backend/app/routers/payment_requests.py` router stub mounted at `/api/requests`
- [ ] T026 Create `backend/seed.py` stub that calls `init_db` only
- [ ] T027 Create `backend/tests/conftest.py` with test DB session and httpx `TestClient` fixtures
- [ ] T028 [P] Create `backend/tests/test_money.py` for amount parsing edge cases
- [ ] T029 Create `frontend/src/api/client.ts` with base URL, `X-User-Email` header, error parsing
- [ ] T030 Create `frontend/src/auth/AuthContext.tsx` with login state persisted to `localStorage`
- [ ] T031 Create `frontend/src/App.tsx` with React Router routes skeleton and auth guard
- [ ] T032 [P] Create `frontend/src/components/Layout.tsx` with nav links and responsive shell
- [ ] T033 [P] Create `frontend/src/styles/global.css` with mobile-first layout tokens
- [ ] T034 Create `frontend/src/main.tsx` entry mounting `App` with `AuthProvider`

**Checkpoint**: `uvicorn app.main:app` starts; empty DB initializes; frontend dev server loads

---

## Phase 3: User Story 1 — Sign In and Request Money (Priority: P1) 🎯 MVP

**Goal**: Mock email login with default wallet/destination; create Pending payment request with share link

**Independent Test**: Log in as new or existing user → create request → receive share URL → see Pending in outgoing list (manual or API)

### Implementation for User Story 1

- [ ] T035 [US1] Implement `POST /api/auth/login` and `GET /api/auth/me` in `backend/app/routers/auth.py` calling wallet/destination ensure
- [ ] T036 [US1] Add login/register schemas and `User` response in `backend/app/schemas.py`
- [ ] T037 [US1] Implement `create_payment_request()` in `backend/app/services/payment_requests.py` — destination validation, snapshot, 7-day `expires_at`, `REQUEST_CREATED` event
- [ ] T038 [US1] Implement `POST /api/requests` in `backend/app/routers/payment_requests.py` per `contracts/openapi.yaml`
- [ ] T039 [US1] Implement `GET /api/payment-destinations/me` in `backend/app/routers/wallets.py` or dedicated router
- [ ] T040 [P] [US1] Create `frontend/src/components/LoginForm.tsx` and `frontend/src/pages/LoginPage.tsx`
- [ ] T041 [P] [US1] Create `frontend/src/components/AmountDisplay.tsx` and `frontend/src/components/StatusBadge.tsx`
- [ ] T042 [P] [US1] Create `frontend/src/components/DestinationSelector.tsx` loading destinations from API
- [ ] T043 [US1] Create `frontend/src/components/CreateRequestForm.tsx` with amount, contact, note, destination validation
- [ ] T044 [US1] Create `frontend/src/pages/CreateRequestPage.tsx` wiring form to `POST /api/requests` and showing share link on success
- [ ] T045 [US1] Wire `/login` and `/requests/new` routes and auth redirect in `frontend/src/App.tsx`
- [ ] T046 [US1] Add minimal `GET /api/requests?direction=outgoing` support in `backend/app/services/payment_requests.py` for MVP verification (full list in US2)

**Checkpoint**: User can log in, create request, copy share link; API returns 403 for another user's `destination_id`

---

## Phase 4: User Story 2 — Manage Requests on Dashboard (Priority: P1)

**Goal**: Dashboard with wallet balance, incoming/outgoing lists, status filter, search, responsive table/cards

**Independent Test**: Seed or create mixed-status requests → filter and search → correct actions per row

### Implementation for User Story 2

- [ ] T047 [US2] Implement full `list_payment_requests()` in `backend/app/services/payment_requests.py` — direction, status, search, incoming match by hash/user id
- [ ] T048 [US2] Call `expire_pending_for_user()` before list response in `backend/app/routers/payment_requests.py`
- [ ] T049 [US2] Implement `GET /api/requests` and `GET /api/wallets/me` response shaping with `can_pay`/`can_decline`/`can_cancel` flags in `backend/app/schemas.py`
- [ ] T050 [P] [US2] Create `frontend/src/components/WalletSummary.tsx` on `frontend/src/pages/DashboardPage.tsx`
- [ ] T051 [P] [US2] Create `frontend/src/components/SearchAndFilterBar.tsx` for status and search query params
- [ ] T052 [P] [US2] Create `frontend/src/components/RequestTable.tsx` for desktop layout in `frontend/src/components/RequestTable.tsx`
- [ ] T053 [P] [US2] Create `frontend/src/components/RequestCard.tsx` for mobile layout in `frontend/src/components/RequestCard.tsx`
- [ ] T054 [US2] Create `frontend/src/components/EmptyState.tsx` and integrate into `frontend/src/pages/DashboardPage.tsx`
- [ ] T055 [US2] Add responsive CSS in `frontend/src/styles/global.css` — table vs cards breakpoint
- [ ] T056 [US2] Wire `/dashboard` route with protected guard in `frontend/src/App.tsx`

**Checkpoint**: Dashboard shows wallet, filtered outgoing/incoming, correct action buttons by status

---

## Phase 5: User Story 3 — Pay an Incoming Request (Priority: P1)

**Goal**: Recipient pays Pending request; atomic wallet credit; 2–3s loading UI; idempotent pay

**Independent Test**: Recipient pays → status PAID → sender wallet balance increases → second pay rejected

### Tests for User Story 3

- [ ] T057 [P] [US3] Add duplicate-pay and wallet-credit assertions in `backend/tests/test_payment_requests.py`

### Implementation for User Story 3

- [ ] T058 [US3] Implement `pay_payment_request()` in `backend/app/services/payment_requests.py` — recipient auth, expiration check, `UPDATE WHERE PENDING`, wallet CREDIT, `wallet_transactions`, `REQUEST_PAID` in one transaction
- [ ] T059 [US3] Implement `POST /api/requests/{id}/pay` in `backend/app/routers/payment_requests.py`
- [ ] T060 [P] [US3] Create `frontend/src/components/LoadingButton.tsx` with 2–3s minimum disabled state
- [ ] T061 [US3] Add Pay action to incoming rows in `frontend/src/components/RequestTable.tsx` and `frontend/src/components/RequestCard.tsx` using `LoadingButton`

**Checkpoint**: Pay flow credits sender wallet once; duplicate pay returns error without second credit

---

## Phase 6: User Story 4 — Decline, Cancel, and View Details (Priority: P2)

**Goal**: Decline/cancel terminal transitions; detail with events; public share page without sensitive fields

**Independent Test**: Decline incoming + cancel outgoing → detail shows events, no actions on terminal; `/r/:token` shows safe summary only

### Tests for User Story 4

- [ ] T062 [P] [US4] Add terminal-state transition rejection tests in `backend/tests/test_payment_requests.py`
- [ ] T063 [P] [US4] Add wrong-destination `403` test for `POST /api/requests` in `backend/tests/test_payment_requests.py`

### Implementation for User Story 4

- [ ] T064 [US4] Implement `decline_payment_request()` and `cancel_payment_request()` in `backend/app/services/payment_requests.py`
- [ ] T065 [US4] Implement `POST /api/requests/{id}/decline` and `POST /api/requests/{id}/cancel` in `backend/app/routers/payment_requests.py`
- [ ] T066 [US4] Implement `get_payment_request_detail()` with events in `backend/app/services/payment_requests.py`
- [ ] T067 [US4] Implement `GET /api/requests/{id}` in `backend/app/routers/payment_requests.py`
- [ ] T068 [US4] Implement `get_public_share_view()` returning `PublicShareView` schema only in `backend/app/services/payment_requests.py`
- [ ] T069 [US4] Implement `GET /api/share/{share_token}` in `backend/app/routers/payment_requests.py`
- [ ] T070 [P] [US4] Create `frontend/src/components/ExpirationCountdown.tsx` for Pending requests
- [ ] T071 [US4] Create `frontend/src/pages/RequestDetailPage.tsx` with actions, events, share link, countdown
- [ ] T072 [P] [US4] Create `frontend/src/pages/ShareRequestPage.tsx` at route `/r/:shareToken`
- [ ] T073 [US4] Wire `/requests/:id` and `/r/:shareToken` in `frontend/src/App.tsx`
- [ ] T074 [US4] Add Decline/Cancel actions to dashboard and detail pages per role rules

**Checkpoint**: Decline, cancel, detail, and public share flows work; terminal requests hide action buttons

---

## Phase 7: User Story 5 — Automatic Expiration (Priority: P2)

**Goal**: Pending requests expire after 7 days on read/action; expired requests reject pay/decline/cancel

**Independent Test**: Seed request with `expires_at` in past → list shows EXPIRED → pay returns clear error

### Implementation for User Story 5

- [ ] T075 [US5] Integrate `expire_pending_for_user()` in `GET /api/requests/{id}` and all mutation handlers in `backend/app/routers/payment_requests.py`
- [ ] T076 [US5] Return `422` with clear message when pay/decline/cancel attempted on EXPIRED in `backend/app/services/payment_requests.py`
- [ ] T077 [US5] Ensure `ExpirationCountdown.tsx` reflects server `expires_at` on `frontend/src/pages/RequestDetailPage.tsx`

**Checkpoint**: Expired requests auto-update on access; mutations blocked with user-friendly errors

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Seed data, static deploy, full test suite, documentation

- [ ] T078 Implement full `backend/seed.py` — users ogulcan/ayca/mehmet, wallets, destinations, requests in all statuses including pre-expired PENDING
- [ ] T079 Update `backend/app/main.py` to serve `frontend/dist` static files and SPA fallback excluding `/api/*`
- [ ] T080 Complete `README.md` — product, stack, Spec-Kit workflow, security model, mock auth limitation, PostgreSQL note, local run, seed, Playwright videos path, Render/Railway deploy
- [ ] T081 [P] Create `e2e/playwright.config.ts` with `video: 'on'` and `webServer` or documented startup
- [ ] T082 Implement `e2e/tests/payment-requests.spec.ts` covering all 10 scenarios from `plan.md`
- [ ] T083 Run `specs/001-p2p-payment-request/quickstart.md` commands and fix any gaps
- [ ] T084 [P] Add production build script notes in `README.md` — `npm run build` + `STATIC_DIR` uvicorn

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)** → **Phase 2 (Foundational)** → **User Stories (3–7)** → **Phase 8 (Polish)**
- **US2** depends on minimal list from T046 (or seed); full dashboard after US1 create flow
- **US3** depends on US2 list UI for Pay button placement (can test via API first)
- **US4** depends on US2 dashboard; detail/share can follow decline/cancel APIs
- **US5** layers on expiration service from Phase 2; wire-up after mutations exist

### User Story Dependencies

| Story | Depends on | Can test independently with |
|-------|------------|-------------------------------|
| US1 | Phase 2 | API-only login + create |
| US2 | Phase 2, US1 (create) or seed | Seed data |
| US3 | US1 requests, US2 UI | Two users + API |
| US4 | US2, US3 patterns | Seed + API |
| US5 | US3–US4 mutations | Seed expired row |

### Parallel Opportunities

- **Phase 1**: T003, T004, T006, T007, T008 in parallel
- **Phase 2**: T014–T016, T023–T024, T028, T032–T033 in parallel after T012
- **US1**: T040–T042 in parallel
- **US2**: T050–T053 in parallel
- **US4**: T062–T063, T070, T072 in parallel
- **Polish**: T081, T084 in parallel

### Parallel Example: User Story 2

```bash
# Frontend components in parallel:
T050 WalletSummary + DashboardPage
T051 SearchAndFilterBar
T052 RequestTable
T053 RequestCard
```

### Parallel Example: Foundational services

```bash
T014 money.py
T015 security.py
T016 events.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 + Phase 2  
2. Complete Phase 3 (US1)  
3. **STOP and VALIDATE**: Login → create request → share link  
4. Demo if ready  

### Incremental Delivery

1. Setup + Foundational → foundation ready  
2. US1 → MVP create flow  
3. US2 → Dashboard  
4. US3 → Pay + wallet credit  
5. US4 → Decline, cancel, detail, share  
6. US5 → Expiration hardening  
7. Polish → seed, E2E, README, deploy  

### Suggested MVP Scope

**User Story 1 only** (Phases 1–3) delivers core “request money” value with API verification; add US2 for usable dashboard before recipient demo.

---

## Notes

- Every task includes a file path; adjust only if plan structure changes  
- Never use float for money — use `backend/app/services/money.py` only  
- Public share responses must use `PublicShareView` — never expose `wallet_id` or `encrypted_identifier`  
- Commit after each phase checkpoint  
- Total tasks: **84** (T001–T084)
