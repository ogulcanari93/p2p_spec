import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ApiError, fetchRequests, payRequest, type PaymentRequestSummary } from "../api/client";
import { LoadingButton } from "../components/LoadingButton";
import { StatusBadge } from "../components/StatusBadge";
import { AmountDisplay } from "../components/AmountDisplay";

/** Placeholder until US4 implements full request detail. */
export function RequestDetailPlaceholder() {
  const { id } = useParams<{ id: string }>();
  const [request, setRequest] = useState<PaymentRequestSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const reload = useCallback(() => setRefreshKey((key) => key + 1), []);

  useEffect(() => {
    if (!id) return;
    setError(null);
    fetchRequests()
      .then((data) => {
        const found =
          data.incoming.find((r) => r.id === id) ?? data.outgoing.find((r) => r.id === id) ?? null;
        setRequest(found);
        if (!found) setError("Request not found.");
      })
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : "Failed to load request."),
      );
  }, [id, refreshKey]);

  const handlePay = async () => {
    if (!id) return;
    try {
      await payRequest(id);
      reload();
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Payment failed.";
      window.alert(message);
    }
  };

  return (
    <div className="card">
      <h1 style={{ marginTop: 0 }}>Request details</h1>
      <p style={{ color: "var(--muted)" }}>
        Full detail view (events, share link, actions) will be implemented in a later phase.
      </p>
      {error && <p className="form-error">{error}</p>}
      {request && (
        <div style={{ marginBottom: "1rem" }}>
          <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", flexWrap: "wrap" }}>
            <AmountDisplay amountMinor={request.amount_minor} currency={request.currency} />
            <StatusBadge status={request.status} />
          </div>
          <p style={{ color: "var(--muted)", margin: "0.5rem 0 0" }}>
            {request.counterparty_label}
          </p>
          {request.can_pay && (
            <LoadingButton
              className="btn btn--primary"
              style={{ marginTop: "1rem" }}
              onClick={handlePay}
            >
              Pay
            </LoadingButton>
          )}
        </div>
      )}
      <Link to="/dashboard" className="btn btn--secondary">
        Back to dashboard
      </Link>
    </div>
  );
}
