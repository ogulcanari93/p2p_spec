import { Link } from "react-router-dom";
import { ApiError, cancelRequest, declineRequest, payRequest, type PaymentRequestSummary } from "../api/client";
import { LoadingButton } from "./LoadingButton";

type Props = {
  request: PaymentRequestSummary;
  direction: "incoming" | "outgoing";
  onRequestUpdated?: () => void;
};

export function RequestActions({ request, direction, onRequestUpdated }: Props) {
  const showPay = direction === "incoming" && request.can_pay;
  const showDecline = direction === "incoming" && request.can_decline;
  const showCancel = direction === "outgoing" && request.can_cancel;

  const runAction = (action: () => Promise<unknown>) => async () => {
    try {
      await action();
      onRequestUpdated?.();
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Action failed.";
      window.alert(message);
    }
  };

  return (
    <div className="request-actions">
      {showPay && (
        <LoadingButton className="btn btn--primary btn--sm" onClick={runAction(() => payRequest(request.id))}>
          Pay
        </LoadingButton>
      )}
      {showDecline && (
        <LoadingButton
          className="btn btn--danger btn--sm"
          onClick={runAction(() => declineRequest(request.id))}
        >
          Decline
        </LoadingButton>
      )}
      {showCancel && (
        <LoadingButton
          className="btn btn--secondary btn--sm"
          onClick={runAction(() => cancelRequest(request.id))}
        >
          Cancel
        </LoadingButton>
      )}
      <Link to={`/requests/${request.id}`} className="btn btn--secondary btn--sm">
        View Details
      </Link>
    </div>
  );
}
