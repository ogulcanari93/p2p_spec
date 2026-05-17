# Data Model: P2P Payment Requests

**Feature**: `001-p2p-payment-request`  
**ORM**: SQLAlchemy 2.x  
**Database**: SQLite (prototype)

## Enums & Constants

### `PaymentRequestStatus`

`PENDING` | `PAID` | `DECLINED` | `EXPIRED` | `CANCELLED`

### `RecipientContactType`

`EMAIL` | `PHONE`

### `RequestEventType`

`REQUEST_CREATED` | `REQUEST_PAID` | `REQUEST_DECLINED` | `REQUEST_CANCELLED` | `REQUEST_EXPIRED`

### `WalletTransactionDirection`

`CREDIT` | `DEBIT`

### `DestinationType` (prototype)

`INTERNAL_WALLET` — only type created in seed/prototype

### `WalletType`

`INTERNAL`

### `EntityStatus` (wallets, destinations)

`ACTIVE` | `INACTIVE`

## State Machine: PaymentRequest

```text
                    ┌─────────────┐
                    │   PENDING   │
                    └──────┬──────┘
           pay (recipient) │ decline (recipient)
           cancel (sender) │ expire (system)
                    ┌──────┴──────┬────────────┬────────────┐
                    ▼             ▼            ▼            ▼
                 PAID        DECLINED     CANCELLED      EXPIRED
              (terminal)    (terminal)    (terminal)    (terminal)
```

- `expires_at = created_at + 7 days` at creation.
- Terminal states: no outgoing transitions.

## Entities

### users

| Column | Type | Constraints |
|--------|------|-------------|
| id | String (UUID) | PK |
| email | String | UNIQUE NOT NULL |
| email_hash | String | UNIQUE NOT NULL |
| display_name | String | NULL |
| phone | String | NULL, UNIQUE |
| phone_hash | String | NULL, UNIQUE |
| created_at | DateTime | NOT NULL UTC |
| updated_at | DateTime | NOT NULL UTC |

**Indexes**: `email`, `email_hash`, `phone_hash` (partial unique when not null)

### wallets

| Column | Type | Constraints |
|--------|------|-------------|
| id | String (UUID) | PK |
| user_id | String | FK → users.id NOT NULL, INDEX |
| currency | String(3) | NOT NULL DEFAULT `TRY`, uppercase |
| wallet_type | String | NOT NULL DEFAULT `INTERNAL` |
| display_name | String | NULL |
| balance_minor | Integer | NOT NULL DEFAULT 0, ≥ 0 |
| available_balance_minor | Integer | NOT NULL DEFAULT 0, ≥ 0 |
| status | String | NOT NULL DEFAULT `ACTIVE` |
| created_at | DateTime | NOT NULL |
| updated_at | DateTime | NOT NULL |

**Prototype rule**: One default TRY internal wallet per user on first login.

### payment_destinations

| Column | Type | Constraints |
|--------|------|-------------|
| id | String (UUID) | PK |
| user_id | String | FK → users.id NOT NULL, INDEX |
| wallet_id | String | FK → wallets.id NULL (required for INTERNAL_WALLET) |
| destination_type | String | NOT NULL |
| currency | String(3) | NOT NULL DEFAULT `TRY` |
| display_label | String | NOT NULL |
| masked_identifier | String | NULL |
| identifier_hash | String | NULL, UNIQUE when present |
| encrypted_identifier | Text | NULL (production bank routing) |
| provider_name | String | NULL |
| provider_account_ref | String | NULL |
| status | String | NOT NULL DEFAULT `ACTIVE` |
| created_at | DateTime | NOT NULL |
| updated_at | DateTime | NOT NULL |

**Prototype**: `destination_type=INTERNAL_WALLET`, `wallet_id` set, `display_label` e.g. "TRY Wallet", `masked_identifier` e.g. "Wallet ••••1234".

**Production fields**: `encrypted_identifier` for recoverable routing; `identifier_hash` for dedup/search only; never log raw values.

### payment_requests

| Column | Type | Constraints |
|--------|------|-------------|
| id | String (UUID) | PK |
| share_token | String | UNIQUE NOT NULL, URL-safe |
| sender_user_id | String | FK → users.id NOT NULL, INDEX |
| recipient_user_id | String | FK → users.id NULL, INDEX |
| recipient_contact | String | NOT NULL |
| recipient_contact_hash | String | NOT NULL, INDEX |
| recipient_contact_type | String | NOT NULL (`EMAIL`\|`PHONE`) |
| destination_id | String | FK → payment_destinations.id NOT NULL |
| destination_snapshot_json | Text/JSON | NOT NULL — safe fields only |
| amount_minor | Integer | NOT NULL, **CHECK > 0** |
| currency | String(3) | NOT NULL DEFAULT `TRY` |
| note | String(280) | NULL |
| status | String | NOT NULL, INDEX |
| created_at | DateTime | NOT NULL |
| updated_at | DateTime | NOT NULL |
| expires_at | DateTime | NOT NULL, INDEX |
| paid_at | DateTime | NULL |
| declined_at | DateTime | NULL |
| cancelled_at | DateTime | NULL |
| expired_at | DateTime | NULL |
| status_reason | String | NULL |

**Invariant**: `destination_id` MUST belong to `sender_user_id` (enforced in service layer + FK join check).

**destination_snapshot_json** shape:

```json
{
  "destination_type": "INTERNAL_WALLET",
  "display_label": "TRY Wallet",
  "masked_identifier": "Wallet ••••0001",
  "currency": "TRY"
}
```

**Incoming match**: `recipient_contact_hash` matches current user's `email_hash` or `phone_hash`, OR `recipient_user_id == current_user.id`.

### request_events

| Column | Type | Constraints |
|--------|------|-------------|
| id | String (UUID) | PK |
| payment_request_id | String | FK → payment_requests.id NOT NULL, INDEX |
| actor_user_id | String | FK → users.id NULL |
| event_type | String | NOT NULL |
| previous_status | String | NULL |
| new_status | String | NULL |
| metadata_json | Text/JSON | NULL — no sensitive IDs |
| ip_address_hash | String | NULL |
| user_agent_hash | String | NULL |
| created_at | DateTime | NOT NULL |

### wallet_transactions

| Column | Type | Constraints |
|--------|------|-------------|
| id | String (UUID) | PK |
| wallet_id | String | FK → wallets.id NOT NULL, INDEX |
| payment_request_id | String | FK → payment_requests.id NULL |
| direction | String | NOT NULL `CREDIT`\|`DEBIT` |
| amount_minor | Integer | NOT NULL, **CHECK > 0** |
| currency | String(3) | NOT NULL |
| status | String | NOT NULL DEFAULT `POSTED` |
| description | String | NULL |
| created_at | DateTime | NOT NULL |

## Validation Rules (service layer)

| Rule | Error |
|------|-------|
| TRY amount: positive, ≤2 decimal places | 422 validation |
| Currency 3-letter uppercase | 422 |
| Note ≤280 chars | 422 |
| Recipient email/phone format | 422 |
| Destination owned by sender | 403 |
| Destination ACTIVE | 422 |
| Destination currency == request currency | 422 |
| Pay/decline: actor is recipient, PENDING, not expired | 403/422 |
| Cancel: actor is sender, PENDING, not expired | 403/422 |
| Terminal status mutation | 422 |

## Relationships (ER)

```text
users 1──* wallets
users 1──* payment_destinations
wallets 1──* payment_destinations (optional FK)
users 1──* payment_requests (as sender)
users 0..1──* payment_requests (as recipient_user)
payment_destinations 1──* payment_requests
payment_requests 1──* request_events
payment_requests 0..1──* wallet_transactions
wallets 1──* wallet_transactions
```

## Seed Data Requirements

| User | Wallet | Destination | Sample requests |
|------|--------|-------------|-----------------|
| ogulcan@example.com | TRY INTERNAL | Active, linked | Mix of statuses |
| ayca@example.com | TRY INTERNAL | Active, linked | Incoming/outgoing with ogulcan |
| mehmet@example.com | TRY INTERNAL | Active, linked | At least one EXPIRED (expires_at in past) |

Include at least one request per terminal status for dashboard demos and E2E filter tests.
