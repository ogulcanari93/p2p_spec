import { Link, useParams } from "react-router-dom";

/** Placeholder until US4 implements full request detail. */
export function RequestDetailPlaceholder() {
  const { id } = useParams<{ id: string }>();

  return (
    <div className="card">
      <h1 style={{ marginTop: 0 }}>Request details</h1>
      <p style={{ color: "var(--muted)" }}>
        Full detail view (events, share link, actions) will be implemented in a later phase.
      </p>
      {id && (
        <p>
          Request ID: <code>{id}</code>
        </p>
      )}
      <Link to="/dashboard" className="btn btn--secondary">
        Back to dashboard
      </Link>
    </div>
  );
}
