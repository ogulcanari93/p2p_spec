# API Contracts

| File | Purpose |
|------|---------|
| [openapi.yaml](./openapi.yaml) | REST contract for FastAPI implementation and frontend `api/client.ts` |

**Prototype auth**: After `POST /api/auth/login`, send `X-User-Email` on protected routes.

**Share safety**: `PublicShareView` intentionally omits `destination_id`, `wallet_id`, `encrypted_identifier`, and `provider_*` fields.
