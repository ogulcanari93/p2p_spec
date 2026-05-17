import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ApiError, fetchRequests, type PaymentRequestSummary } from "../api/client";
import { EmptyState } from "../components/EmptyState";
import { RequestCard } from "../components/RequestCard";
import { RequestTable } from "../components/RequestTable";
import { SearchAndFilterBar } from "../components/SearchAndFilterBar";
import { WalletSummary } from "../components/WalletSummary";

function RequestSection({
  title,
  description,
  requests,
  direction,
  loading,
}: {
  title: string;
  description: string;
  requests: PaymentRequestSummary[];
  direction: "incoming" | "outgoing";
  loading: boolean;
}) {
  return (
    <section className="card dashboard-section">
      <h2 style={{ marginTop: 0 }}>{title}</h2>
      <p style={{ color: "var(--muted)", marginTop: 0 }}>{description}</p>
      {loading && <p style={{ color: "var(--muted)" }}>Loading…</p>}
      {!loading && requests.length === 0 && (
        <EmptyState
          title={`No ${direction} requests`}
          description="Try changing the status filter or search, or create a new request."
        />
      )}
      {!loading && requests.length > 0 && (
        <>
          <RequestTable requests={requests} direction={direction} />
          <div className="request-card-list hide-desktop">
            {requests.map((r) => (
              <RequestCard key={r.id} request={r} direction={direction} />
            ))}
          </div>
        </>
      )}
    </section>
  );
}

export function DashboardPage() {
  const [status, setStatus] = useState("all");
  const [searchInput, setSearchInput] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [outgoing, setOutgoing] = useState<PaymentRequestSummary[]>([]);
  const [incoming, setIncoming] = useState<PaymentRequestSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = window.setTimeout(() => setSearchQuery(searchInput.trim()), 300);
    return () => window.clearTimeout(timer);
  }, [searchInput]);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchRequests({ status, search: searchQuery || undefined })
      .then((data) => {
        setOutgoing(data.outgoing);
        setIncoming(data.incoming);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load requests"))
      .finally(() => setLoading(false));
  }, [status, searchQuery]);

  return (
    <div className="dashboard">
      <div className="dashboard__header card">
        <h1 style={{ marginTop: 0 }}>Dashboard</h1>
        <p style={{ color: "var(--muted)", marginTop: 0 }}>
          Manage incoming and outgoing payment requests.
        </p>
        <Link to="/requests/new" className="btn btn--primary">
          New request
        </Link>
      </div>

      <WalletSummary />

      <SearchAndFilterBar
        status={status}
        search={searchInput}
        onStatusChange={setStatus}
        onSearchChange={setSearchInput}
      />

      {error && <p className="form-error card">{error}</p>}

      <RequestSection
        title="Incoming requests"
        description="Requests others sent to you."
        requests={incoming}
        direction="incoming"
        loading={loading}
      />

      <RequestSection
        title="Outgoing requests"
        description="Requests you sent to others."
        requests={outgoing}
        direction="outgoing"
        loading={loading}
      />
    </div>
  );
}
