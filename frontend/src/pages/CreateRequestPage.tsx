import { useState } from "react";
import { Link } from "react-router-dom";
import type { CreateRequestResponse } from "../api/client";
import { CreateRequestForm } from "../components/CreateRequestForm";
import { ReferenceCode } from "../components/ReferenceCode";

export function CreateRequestPage() {
  const [created, setCreated] = useState<CreateRequestResponse | null>(null);

  if (created) {
    const { request, share_url: shareUrl } = created;
    return (
      <div className="card create-success">
        <h1>Request created</h1>
        <ReferenceCode code={request.reference_code} />
        <p style={{ color: "var(--muted)", marginTop: 0 }}>
          Use this ID to track the request in your dashboard or when contacting support.
        </p>
        <p>Share this link with your friend:</p>
        <p>
          <a href={shareUrl} target="_blank" rel="noreferrer" data-testid="create-share-link">
            {shareUrl}
          </a>
        </p>
        <p style={{ color: "var(--muted)" }}>
          The request is pending for 7 days. You can see it on your dashboard.
        </p>
        <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
          <Link to={`/requests/${request.id}`} className="btn btn--secondary">
            View details
          </Link>
          <Link to="/dashboard" className="btn btn--primary">
            Go to dashboard
          </Link>
          <button type="button" className="btn btn--secondary" onClick={() => setCreated(null)}>
            Create another
          </button>
        </div>
      </div>
    );
  }

  return <CreateRequestForm onCreated={setCreated} />;
}
