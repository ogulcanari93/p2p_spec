# Feature Specification: P2P Payment Requests

**Feature Branch**: `001-p2p-payment-request`

**Created**: 2026-05-17

**Status**: Draft

**Input**: User description: Build a responsive consumer fintech web application that allows authenticated users to request money from friends (similar to Venmo Request or Cash App payment requests), with mock email login, internal wallet destinations, full request lifecycle management, simulated payment fulfillment, and safe handling of payout destination data.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Sign In and Request Money (Priority: P1)

As an authenticated user, I want to log in with my email and create a payment request to a friend so they can pay me into my chosen payout destination.

**Why this priority**: Creating and sharing a request is the core product value; without it, no other flows matter.

**Independent Test**: A user logs in (new or existing), confirms a default wallet and destination exist, creates a request with amount and recipient contact, and receives a shareable link while the request appears as Pending in outgoing requests.

**Acceptance Scenarios**:

1. **Given** a user enters an email on the login screen, **When** the email matches an existing account, **Then** the user is signed in and lands on the dashboard.
2. **Given** a user enters an email that does not exist, **When** they submit login, **Then** a new user account is created, a default TRY internal wallet is created if missing, a default active internal-wallet payment destination is created if missing, and the user is signed in.
3. **Given** an authenticated user on the create-request flow, **When** they enter a valid recipient contact (email or phone), a valid positive amount in TRY (up to two decimal places), optional note (≤280 characters), and optional destination, **Then** a Pending payment request is created with a unique share link, safe destination snapshot, 7-day expiration, and a request-created audit event.
4. **Given** no destination is selected, **When** the user submits a valid request, **Then** the system uses the user's default active destination for the request currency.
5. **Given** the user selects a destination, **When** it is not owned by them, not ACTIVE, or currency mismatches the request, **Then** creation is rejected with a clear error and no request is created.
6. **Given** invalid amount (zero, negative, non-numeric, or more than two decimal places for TRY), **When** the user submits, **Then** a user-friendly validation error is shown.

---

### User Story 2 - Manage Requests on Dashboard (Priority: P1)

As a user, I want a single dashboard showing my wallet balance, outgoing requests I sent, and incoming requests addressed to me, with filtering and search, so I can track and act on requests quickly.

**Why this priority**: Ongoing visibility and actions on lists is essential for daily use after creation.

**Independent Test**: A user opens the dashboard, sees wallet summary, outgoing and incoming sections, filters by status, searches by sender/recipient/note, and sees correct actions per request state and direction.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** they open the dashboard, **Then** they see their default wallet balance (for demonstration), outgoing requests (they are sender), and incoming requests (their email or phone matches recipient contact or they are the linked recipient user).
2. **Given** requests in various statuses, **When** the user filters by All, Pending, Paid, Declined, Expired, or Cancelled, **Then** only matching requests appear in the relevant section.
3. **Given** multiple requests, **When** the user searches by sender email, recipient contact, or note, **Then** matching requests are shown.
4. **Given** an incoming Pending request, **When** viewed in the list, **Then** Pay, Decline, and View Details actions are available.
5. **Given** an outgoing Pending request, **When** viewed in the list, **Then** Cancel and View Details actions are available.
6. **Given** a request in a terminal status (Paid, Declined, Expired, Cancelled), **When** viewed in the list, **Then** only View Details is available.
7. **Given** list layout on a wide screen, **When** the dashboard renders, **Then** requests display in a table-oriented layout; on narrow screens, card-oriented layout preserves usable primary actions.

---

### User Story 3 - Pay an Incoming Request (Priority: P1)

As the recipient of a Pending request, I want to pay it through a simulated payment flow so the sender receives funds in their designated destination.

**Why this priority**: Fulfillment completes the money-request loop and validates the destination model.

**Independent Test**: Recipient logs in, pays a Pending incoming request, sees a brief loading state, request becomes Paid, sender's wallet balance increases by the request amount, and duplicate pay attempts do not double-credit.

**Acceptance Scenarios**:

1. **Given** an incoming Pending request not expired, **When** the recipient taps Pay, **Then** the pay action shows a loading state for approximately 2–3 seconds with the button disabled.
2. **Given** Pay completes successfully, **When** the recipient refreshes or returns to the dashboard, **Then** the request status is Paid with paid timestamp visible.
3. **Given** Pay completes and the destination is an internal wallet, **When** the transaction commits, **Then** the sender's destination wallet is credited by the request amount in the same atomic operation as status update, and a wallet transaction record is created.
4. **Given** the sender views their dashboard after payment, **When** they refresh, **Then** the same request shows Paid and wallet balance reflects the credit.
5. **Given** the recipient taps Pay multiple times rapidly, **When** the first payment succeeds, **Then** subsequent attempts do not create duplicate payments, wallet credits, or invalid status transitions.

---

### User Story 4 - Decline, Cancel, and View Details (Priority: P2)

As a recipient or sender, I want to decline, cancel, or inspect request details and history so I can resolve requests I do not intend to pay or no longer want open.

**Why this priority**: Secondary lifecycle actions and transparency build trust and reduce support burden.

**Independent Test**: Recipient declines one Pending request; sender cancels another; both become terminal; detail view shows lifecycle events and hides state-changing buttons for terminal requests.

**Acceptance Scenarios**:

1. **Given** an incoming Pending request addressed to the current user and not expired, **When** they Decline, **Then** status becomes Declined (terminal), declined timestamp is set, and a request-declined event is recorded.
2. **Given** an outgoing Pending request created by the current user and not expired, **When** they Cancel, **Then** status becomes Cancelled (terminal), cancelled timestamp is set, and a request-cancelled event is recorded.
3. **Given** a request detail view, **When** opened by an authorized user, **Then** it shows amount, currency, note, sender info, recipient contact, linked recipient user if known, status, created and expiration times, shareable link, expiration countdown for Pending, safe destination snapshot, and lifecycle event history when available.
4. **Given** a Paid, Declined, Expired, or Cancelled request, **When** detail is viewed, **Then** no Pay, Decline, or Cancel actions are shown.
5. **Given** a public share link (share token), **When** an unauthenticated or any viewer opens it, **Then** a limited summary is shown without internal wallet IDs, encrypted identifiers, provider references, or full destination details.

---

### User Story 5 - Automatic Expiration (Priority: P2)

As the system, I want Pending requests to expire after seven days so stale requests cannot be paid or acted on indefinitely.

**Why this priority**: Expiration protects senders and recipients from ambiguous open obligations; prototype evaluates on read/action with production noted for scheduled jobs.

**Independent Test**: A Pending request older than seven days is shown as Expired; pay, decline, and cancel are rejected with clear errors.

**Acceptance Scenarios**:

1. **Given** a Pending request where current time is on or after expires_at (created_at + 7 days), **When** dashboard, detail, or any state-changing action is processed, **Then** status becomes Expired first, expired_at is set, and a request-expired event is written if not already expired.
2. **Given** an Expired request, **When** a user attempts Pay, Decline, or Cancel, **Then** the action is rejected with a clear error.
3. **Given** a Pending request not yet expired, **When** detail is viewed, **Then** an expiration countdown is displayed.

---

### Edge Cases

- Recipient contact is email vs phone: system infers contact type and hashes contact for lookup; invalid format returns user-friendly validation error.
- Recipient has no account yet: request is stored with contact only; when a user registers/logs in with matching email or phone, request appears in incoming list.
- User has no active destination for currency: request creation fails with clear error.
- Sender attempts to pay their own outgoing request: rejected (only recipient may pay).
- Non-recipient attempts Pay or Decline: rejected with unauthorized error.
- Non-sender attempts Cancel: rejected with unauthorized error.
- Terminal request (Paid, Declined, Expired, Cancelled): any pay/decline/cancel rejected.
- Concurrent pay from two sessions: only one succeeds; no duplicate wallet credit.
- Note at 280 characters: accepted; 281+: rejected.
- Share page must never leak sensitive destination fields even if snapshot exists on server.
- Audit logs and events must not contain raw card, CVV, bank credentials, IBAN, or recoverable sensitive routing values.

## Requirements *(mandatory)*

### Functional Requirements

**Authentication & onboarding**

- **FR-001**: System MUST allow sign-in via email only (mock authentication): existing users log in; unknown emails create a user record.
- **FR-002**: On first login for a user, system MUST ensure a default TRY internal wallet exists and a default active payment destination pointing to that wallet exists.
- **FR-003**: Protected operations MUST identify the current user server-side (prototype mechanism such as session or client-provided user email header); production-grade authentication is out of scope but MUST be documented as a limitation.

**Payment destinations & wallets**

- **FR-004**: Every payment request MUST reference a payment destination owned by the requester; system MUST NEVER allow a request that pays into another user's destination.
- **FR-005**: For this prototype, payment destinations MUST be internal wallet references only; system MUST NOT collect raw card numbers, CVV, real bank credentials, or real IBAN data.
- **FR-006**: Data model MUST support future production payout destinations: encrypted identifiers for recoverable routing values, identifier hashes for duplicate detection/lookup only (not recovery), masked identifiers for display.
- **FR-007**: Dashboard MUST show the current user's default wallet balance for demonstration.

**Request creation**

- **FR-008**: Authenticated users MUST create payment requests with recipient contact (email or phone), amount, currency (default TRY), optional note (≤280 chars), and optional destination selection.
- **FR-009**: Backend MUST validate destination belongs to requester, is ACTIVE, and matches request currency; default active destination used when none selected.
- **FR-010**: Amounts MUST be accepted as decimal strings in UI, parsed precisely on server, stored as integer minor units; TRY amounts MUST reject zero, negative, non-numeric, or more than two decimal places.
- **FR-011**: Each request MUST have unique internal id, unique share token, destination_id, destination_snapshot_json (safe fields only: destination_type, display_label, masked_identifier, currency), PENDING initial status, and expires_at exactly 7 days after creation.
- **FR-012**: Successful creation MUST return a shareable link and record a REQUEST_CREATED event.

**Request listing & discovery**

- **FR-013**: Users MUST list requests with direction (outgoing as sender, incoming as matching recipient contact or recipient user), optional status filter (All, Pending, Paid, Declined, Expired, Cancelled), and search across sender email, recipient contact, and note.
- **FR-014**: Outgoing list items MUST include counterparty, amount, currency, status, created time, expiration state, and safe destination display.

**Request detail & sharing**

- **FR-015**: Authorized users MUST view full request detail including lifecycle events when available.
- **FR-016**: Public share-token view MUST show limited summary only; MUST NOT expose internal wallet IDs, encrypted identifiers, provider references, or full destination details.

**Payment fulfillment (simulated)**

- **FR-017**: Only the recipient MAY pay an incoming Pending, non-expired request after server-side authorization and validation.
- **FR-018**: Pay flow MUST show client loading state ~2–3 seconds; server MUST revalidate status, expiration, and destination before marking PAID, setting paid_at, writing REQUEST_PAID, crediting sender's internal wallet in the same transaction, and creating a wallet transaction (CREDIT, POSTED).
- **FR-019**: Duplicate pay attempts MUST NOT duplicate credits or violate state machine.

**Decline & cancel**

- **FR-020**: Recipient MUST decline incoming Pending non-expired requests → DECLINED (terminal), declined_at, REQUEST_DECLINED.
- **FR-021**: Sender MUST cancel outgoing Pending non-expired requests → CANCELLED (terminal), cancelled_at, REQUEST_CANCELLED.

**Expiration**

- **FR-022**: Before dashboard responses, detail responses, and state-changing actions, system MUST evaluate expiration: if Pending and now ≥ expires_at → EXPIRED, expired_at, REQUEST_EXPIRED.
- **FR-023**: Expired requests MUST NOT be paid, declined, or cancelled.

**Status model**

- **FR-024**: Statuses MUST be PENDING, PAID, DECLINED, EXPIRED, CANCELLED with allowed transitions only: PENDING→PAID (recipient pay), PENDING→DECLINED (recipient), PENDING→CANCELLED (sender), PENDING→EXPIRED (system); no transitions from terminal states.

**Security, privacy & authorization**

- **FR-025**: All state-changing actions MUST be authorized server-side.
- **FR-026**: Logs and audit events MUST NOT contain raw sensitive financial identifiers.
- **FR-027**: Unauthorized actions MUST return forbidden; missing resources not found; invalid terminal/expired actions clear errors; invalid amount/contact user-friendly validation; wrong user's destination forbidden.

**Capabilities (user-facing operations)**

- **FR-028**: Users MUST sign in and retrieve current profile.
- **FR-029**: Users MUST retrieve their wallets and payment destinations.
- **FR-030**: Users MUST create, list (filtered), and retrieve payment requests; retrieve public share view by token.
- **FR-031**: Users MUST pay, decline, or cancel requests per rules above.

**Demonstration data**

- **FR-032**: Seed data MUST include users ogulcan@example.com, ayca@example.com, mehmet@example.com each with default TRY wallet and internal destination, plus sample requests in Pending, Paid, Declined, Expired, and Cancelled states.

**Quality & verification**

- **FR-033**: Automated end-to-end tests MUST cover: login and default wallet/destination; create request; outgoing Pending; recipient pay with loading and Paid status; sender sees Paid and wallet credit; decline; cancel; expired not payable; dashboard filter and search.
- **FR-034**: Automated backend tests MUST cover: cannot use another user's destination; duplicate pay does not duplicate credit; terminal transitions rejected.

### Key Entities

- **User**: Person identified by unique email (and optional phone); display name; hashed email/phone for lookup; timestamps.
- **Wallet**: User-owned balance container (currency, type INTERNAL for prototype, balance in minor units, status).
- **Payment destination**: Where money should go for a request; owned by user; links to wallet for prototype; supports future bank-style fields (masked display, hash for lookup, encrypted recoverable identifier, provider metadata); ACTIVE/ inactive status; currency and display label.
- **Payment request**: Money ask from sender to recipient contact; references sender's destination; stores safe destination snapshot; amount in minor units; optional note; status and lifecycle timestamps (paid, declined, cancelled, expired); share token for public link; expiration.
- **Request event**: Immutable audit of lifecycle (type, actor, previous/new status, safe metadata, hashed client fingerprints—not raw sensitive data).
- **Wallet transaction**: Ledger entry for CREDIT/DEBIT against a wallet, optionally linked to a payment request.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new user can log in, create a payment request, and obtain a share link in under 2 minutes without assistance.
- **SC-002**: 100% of payment requests in the system reference a destination owned by the requester (verifiable by data rules and tests).
- **SC-003**: Recipients can complete simulated payment on a Pending request and both parties see Paid status and correct sender wallet credit on next refresh.
- **SC-004**: Duplicate pay attempts on the same request result in exactly one wallet credit in automated tests.
- **SC-005**: Pending requests automatically show as Expired after 7 days when viewed or acted upon; expired requests cannot be paid in tests.
- **SC-006**: Public share pages expose zero internal wallet or encrypted routing identifiers in manual and automated checks.
- **SC-007**: Dashboard status filter and search return correct subsets in end-to-end tests for seeded data.
- **SC-008**: Core flows (login, create, list, pay, decline, cancel, detail, share view) are usable on mobile-width and desktop-width viewports without blocking primary actions.

## Assumptions

- **Target market**: Consumer fintech prototype focused on TRY; multi-currency display may exist but TRY validation rules apply as specified.
- **Authentication**: Mock email-only login is acceptable for prototype; README will state production auth is required before launch.
- **Payments**: No real payment rails; fulfillment is simulated wallet credit only.
- **Expiration processing**: Evaluated on read and state-changing actions for prototype; production should use a scheduled worker (documented in README).
- **Recipient matching**: Incoming requests match logged-in user's email or phone against recipient_contact or linked recipient_user_id.
- **Deployment**: Single deployable unit may serve web UI and API together; exact hosting is an implementation decision captured in the implementation plan.
- **Project constraints (stakeholder-mandated for implementation phase)**: Responsive web client, API backend with ORM persistence, SQLite for prototype database, end-to-end tests with video recording, and backend serving production web assets—these inform `/speckit-plan` but are not success metrics for end users.
- **Documentation**: README will cover product overview, stack, Spec-Kit artifacts, wallet/destination model, security model, local run, seeding, E2E videos location, deployment, and known limitations.
