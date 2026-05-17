import { useState } from "react";
import { Link } from "react-router-dom";
import { CreateRequestForm } from "../components/CreateRequestForm";

export function CreateRequestPage() {
  const [shareUrl, setShareUrl] = useState<string | null>(null);

  if (shareUrl) {
    return (
      <div className="card">
        <h1>Request created</h1>
        <p>Share this link with your friend:</p>
        <p>
          <a href={shareUrl} target="_blank" rel="noreferrer">
            {shareUrl}
          </a>
        </p>
        <p style={{ color: "var(--muted)" }}>
          The request is pending for 7 days. You can see it on your dashboard.
        </p>
        <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
          <Link to="/dashboard" className="btn btn--primary">
            Go to dashboard
          </Link>
          <button type="button" className="btn btn--secondary" onClick={() => setShareUrl(null)}>
            Create another
          </button>
        </div>
      </div>
    );
  }

  return <CreateRequestForm onCreated={setShareUrl} />;
}
