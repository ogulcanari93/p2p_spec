import { Link } from "react-router-dom";
import type { PaymentRequestSummary } from "../api/client";

type Props = {
  request: PaymentRequestSummary;
  direction: "incoming" | "outgoing";
};

function stubAction(label: string) {
  window.alert(`${label} will be available in a future update.`);
}

export function RequestActions({ request, direction }: Props) {
  const showIncomingPending = direction === "incoming" && request.can_pay;
  const showOutgoingPending = direction === "outgoing" && request.can_cancel;

  return (
    <div className="request-actions">
      {showIncomingPending && (
        <>
          <button type="button" className="btn btn--primary btn--sm" onClick={() => stubAction("Pay")}>
            Pay
          </button>
          <button
            type="button"
            className="btn btn--danger btn--sm"
            onClick={() => stubAction("Decline")}
          >
            Decline
          </button>
        </>
      )}
      {showOutgoingPending && (
        <button type="button" className="btn btn--secondary btn--sm" onClick={() => stubAction("Cancel")}>
          Cancel
        </button>
      )}
      <Link to={`/requests/${request.id}`} className="btn btn--secondary btn--sm">
        View Details
      </Link>
    </div>
  );
}
