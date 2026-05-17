import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import {
  ApiError,
  fetchPublicShare,
  fetchRequests,
  type PublicShareView,
} from "../api/client";
import { AmountDisplay } from "../components/AmountDisplay";
import { ReferenceCode } from "../components/ReferenceCode";
import { StatusBadge } from "../components/StatusBadge";

export function ShareRequestPage() {
  const { shareToken } = useParams<{ shareToken: string }>();
  const { user } = useAuth();
  const [share, setShare] = useState<PublicShareView | null>(null);
  const [detailRequestId, setDetailRequestId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!shareToken) return;
    setError(null);
    fetchPublicShare(shareToken)
      .then(setShare)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Share link not found."));
  }, [shareToken]);

  useEffect(() => {
    if (!user || !shareToken) {
      setDetailRequestId(null);
      return;
    }
    fetchRequests()
      .then((data) => {
        const match =
          data.incoming.find((r) => r.share_token === shareToken) ??
          data.outgoing.find((r) => r.share_token === shareToken);
        setDetailRequestId(match?.id ?? null);
      })
      .catch(() => setDetailRequestId(null));
  }, [user, shareToken]);

  if (error) {
    return (
      <div className="layout">
        <div className="card">
          <p className="form-error">{error}</p>
          <Link to="/login" className="btn btn--primary">
            Log in
          </Link>
        </div>
      </div>
    );
  }

  if (!share) {
    return (
      <div className="layout">
        <div className="card">
          <p style={{ color: "var(--muted)" }}>Loading…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="layout">
      <div className="card share-page" data-testid="share-page">
        <h1 style={{ marginTop: 0 }}>Payment request</h1>
        <ReferenceCode code={share.reference_code} />
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", flexWrap: "wrap" }}>
          <AmountDisplay amountMinor={share.amount_minor} currency={share.currency} />
          <StatusBadge status={share.status} />
        </div>
        <dl className="request-detail__meta">
          <dt>From</dt>
          <dd>{share.sender_display}</dd>
          <dt>To</dt>
          <dd>{share.recipient_contact_masked}</dd>
          {share.note && (
            <>
              <dt>Note</dt>
              <dd>{share.note}</dd>
            </>
          )}
          <dt>Created</dt>
          <dd>{new Date(share.created_at).toLocaleString()}</dd>
          <dt>Expires</dt>
          <dd>{new Date(share.expires_at).toLocaleString()}</dd>
        </dl>

        {user ? (
          detailRequestId ? (
            <Link
              to={`/requests/${detailRequestId}`}
              className="btn btn--primary"
              data-testid="share-open-details"
            >
              Open full details
            </Link>
          ) : (
            <p style={{ color: "var(--muted)" }}>
              You are logged in. This request is not in your dashboard lists.
            </p>
          )
        ) : (
          <p style={{ color: "var(--muted)" }}>
            <Link to="/login">Log in</Link> to pay or manage this request if you are the recipient.
          </p>
        )}
      </div>
    </div>
  );
}
