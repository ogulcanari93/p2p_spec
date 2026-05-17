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
import { EventHistory } from "../components/EventHistory";
import { ExpirationCountdown } from "../components/ExpirationCountdown";
import { LoadingButton } from "../components/LoadingButton";
import { StatusBadge } from "../components/StatusBadge";

export function RequestDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [request, setRequest] = useState<PaymentRequestDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    if (!id) return;
    setError(null);
    fetchRequestDetail(id)
      .then(setRequest)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load request."));
  }, [id]);

  const handleAction = async (action: () => Promise<PaymentRequestDetail>) => {
    if (!id) return;
    try {
      const updated = await action();
      setRequest(updated);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Action failed.";
      window.alert(message);
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

  const displayStatus =
    request.is_expired && request.status === "PENDING" ? "EXPIRED" : request.status;

  return (
    <div className="card request-detail">
      <div className="request-detail__header">
        <h1 style={{ marginTop: 0 }}>Request details</h1>
        <StatusBadge status={displayStatus} />
      </div>

      <p style={{ fontSize: "1.5rem", margin: "0.5rem 0" }}>
        <AmountDisplay amountMinor={request.amount_minor} currency={request.currency} />
      </p>

      <ExpirationCountdown expiresAt={request.expires_at} status={request.status} />

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
          <LoadingButton
            className="btn btn--primary"
            onClick={() => handleAction(() => payRequest(request.id))}
          >
            Pay
          </LoadingButton>
        )}
        {request.can_decline && (
          <LoadingButton
            className="btn btn--danger"
            onClick={() => handleAction(() => declineRequest(request.id))}
          >
            Decline
          </LoadingButton>
        )}
        {request.can_cancel && (
          <LoadingButton
            className="btn btn--secondary"
            onClick={() => handleAction(() => cancelRequest(request.id))}
          >
            Cancel
          </LoadingButton>
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
