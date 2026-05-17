import { Link } from "react-router-dom";
import { ApiError, payRequest, type PaymentRequestSummary } from "../api/client";
import { LoadingButton } from "./LoadingButton";

type Props = {
  request: PaymentRequestSummary;
  direction: "incoming" | "outgoing";
  onRequestUpdated?: () => void;
};

function stubAction(label: string) {
  window.alert(`${label} will be available in a future update.`);
}

export function RequestActions({ request, direction, onRequestUpdated }: Props) {
  const showIncomingPending = direction === "incoming" && request.can_pay;
  const showOutgoingPending = direction === "outgoing" && request.can_cancel;

  const handlePay = async () => {
    try {
      await payRequest(request.id);
      onRequestUpdated?.();
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Payment failed.";
      window.alert(message);
    }
  };

  return (
    <div className="request-actions">
      {showIncomingPending && (
        <>
          <LoadingButton className="btn btn--primary btn--sm" onClick={handlePay}>
            Pay
          </LoadingButton>
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
