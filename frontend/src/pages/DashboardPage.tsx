import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ApiError, fetchOutgoingRequests, type PaymentRequestSummary } from "../api/client";
import { AmountDisplay } from "../components/AmountDisplay";
import { StatusBadge } from "../components/StatusBadge";

/** Minimal dashboard shell for US1 — full dashboard in US2. */
export function DashboardPage() {
  const [outgoing, setOutgoing] = useState<PaymentRequestSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOutgoingRequests()
      .then((data) => setOutgoing(data.outgoing))
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load requests"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="card" style={{ marginBottom: "1rem" }}>
        <h1>Dashboard</h1>
        <p style={{ color: "var(--muted)", marginTop: 0 }}>
          Welcome. Create a request or review your outgoing requests below.
        </p>
        <Link to="/requests/new" className="btn btn--primary">
          New request
        </Link>
      </div>

      <section className="card">
        <h2>Outgoing requests</h2>
        {loading && <p style={{ color: "var(--muted)" }}>Loading…</p>}
        {error && <p className="form-error">{error}</p>}
        {!loading && !error && outgoing.length === 0 && (
          <p style={{ color: "var(--muted)" }}>No outgoing requests yet.</p>
        )}
        {!loading && outgoing.length > 0 && (
          <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
            {outgoing.map((r) => (
              <li
                key={r.id}
                style={{
                  padding: "0.75rem 0",
                  borderBottom: "1px solid var(--border)",
                }}
              >
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", alignItems: "center" }}>
                  <AmountDisplay amountMinor={r.amount_minor} currency={r.currency} />
                  <StatusBadge status={r.status} />
                  <span style={{ color: "var(--muted)" }}>→ {r.recipient_contact}</span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
