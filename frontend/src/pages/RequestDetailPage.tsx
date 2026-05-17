import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  ApiError,
  cancelRequest,
  declineRequest,
  fetchRequestDetail,
  payRequest,
  type PaymentRequestDetail,
} from "../api/client";
import { AmountDisplay } from "../components/AmountDisplay";
import { ReferenceCode } from "../components/ReferenceCode";
import { EventHistory } from "../components/EventHistory";
import { ExpirationCountdown } from "../components/ExpirationCountdown";
import { StatusBadge } from "../components/StatusBadge";
import {
  CANCEL_ACTION,
  DECLINE_ACTION,
  PAY_ACTION,
  useRequestAction,
} from "../context/RequestActionContext";
import { resolveDisplayStatus } from "../utils/expiration";

export function RequestDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [request, setRequest] = useState<PaymentRequestDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { runRequestAction, busy } = useRequestAction();

  useEffect(() => {
    if (!id) return;
    setError(null);
    fetchRequestDetail(id)
      .then(setRequest)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load request."));
  }, [id]);

  const handleAction = async (
    config: typeof PAY_ACTION,
    action: () => Promise<PaymentRequestDetail>,
  ) => {
    if (!id) return;
    try {
      const updated = await runRequestAction(config, action);
      setRequest(updated);
    } catch {
      /* alert handled in context */
    }
  };

  if (error) {
    return (
      <div className="card">
        <p className="form-error">{error}</p>
        <Link to="/dashboard" className="btn btn--secondary">
          Back to dashboard
        </Link>
      </div>
    );
  }

  if (!request) {
    return (
      <div className="card">
        <p style={{ color: "var(--muted)" }}>Loading request…</p>
      </div>
    );
  }

  const displayStatus = resolveDisplayStatus(request.status, request.is_expired);

  return (
    <div className="card request-detail">
      <div className="request-detail__header">
        <h1 style={{ marginTop: 0 }}>Request details</h1>
        <StatusBadge status={displayStatus} />
      </div>
      <ReferenceCode code={request.reference_code} />

      <p style={{ fontSize: "1.5rem", margin: "0.5rem 0" }}>
        <AmountDisplay amountMinor={request.amount_minor} currency={request.currency} />
      </p>

      <ExpirationCountdown
        expiresAt={request.expires_at}
        status={request.status}
        isExpired={request.is_expired}
      />

      <dl className="request-detail__meta">
        <dt>Sender</dt>
        <dd>{request.sender?.display_name ?? request.sender?.email ?? "—"}</dd>
        <dt>Recipient contact</dt>
        <dd>{request.recipient_contact}</dd>
        {request.recipient_user_id && (
          <>
            <dt>Linked recipient</dt>
            <dd>Registered user</dd>
          </>
        )}
        <dt>Note</dt>
        <dd>{request.note ?? "—"}</dd>
        <dt>Created</dt>
        <dd>{new Date(request.created_at).toLocaleString()}</dd>
        <dt>Expires</dt>
        <dd>{new Date(request.expires_at).toLocaleString()}</dd>
        <dt>Destination</dt>
        <dd>
          {request.destination_snapshot.display_label}
          {request.destination_snapshot.masked_identifier &&
            ` · ${request.destination_snapshot.masked_identifier}`}
        </dd>
        <dt>Share link</dt>
        <dd>
          <a href={request.share_url} target="_blank" rel="noreferrer">
            {request.share_url}
          </a>
        </dd>
      </dl>

      <div className="request-actions" style={{ marginBottom: "1.5rem" }}>
        {request.can_pay && (
          <button
            type="button"
            className="btn btn--primary"
            data-testid="detail-pay-button"
            disabled={busy}
            onClick={() => void handleAction(PAY_ACTION, () => payRequest(request.id))}
          >
            Pay
          </button>
        )}
        {request.can_decline && (
          <button
            type="button"
            className="btn btn--danger"
            disabled={busy}
            onClick={() => void handleAction(DECLINE_ACTION, () => declineRequest(request.id))}
          >
            Decline
          </button>
        )}
        {request.can_cancel && (
          <button
            type="button"
            className="btn btn--secondary"
            disabled={busy}
            onClick={() => void handleAction(CANCEL_ACTION, () => cancelRequest(request.id))}
          >
            Cancel
          </button>
        )}
        <Link to="/dashboard" className="btn btn--secondary">
          Back to dashboard
        </Link>
      </div>

      <section>
        <h2 style={{ fontSize: "1rem" }}>Event history</h2>
        <EventHistory events={request.events} />
      </section>
    </div>
  );
}
