import { Link } from "react-router-dom";
import { cancelRequest, declineRequest, payRequest, type PaymentRequestSummary } from "../api/client";
import {
  CANCEL_ACTION,
  DECLINE_ACTION,
  PAY_ACTION,
  useRequestAction,
} from "../context/RequestActionContext";

type Props = {
  request: PaymentRequestSummary;
  direction: "incoming" | "outgoing";
  onRequestUpdated?: () => void;
};

export function RequestActions({ request, direction, onRequestUpdated }: Props) {
  const { runRequestAction, busy } = useRequestAction();
  const showPay = direction === "incoming" && request.can_pay;
  const showDecline = direction === "incoming" && request.can_decline;
  const showCancel = direction === "outgoing" && request.can_cancel;

  const wrap = (config: typeof PAY_ACTION, action: () => Promise<unknown>) => async () => {
    try {
      await runRequestAction(config, action);
      onRequestUpdated?.();
    } catch {
      /* errors shown via alert in runRequestAction */
    }
  };

  return (
    <div className="request-actions">
      {showPay && (
        <button
          type="button"
          className="btn btn--primary btn--sm"
          data-testid="pay-button"
          disabled={busy}
          onClick={() => void wrap(PAY_ACTION, () => payRequest(request.id))()}
        >
          Pay
        </button>
      )}
      {showDecline && (
        <button
          type="button"
          className="btn btn--danger btn--sm"
          data-testid="decline-button"
          disabled={busy}
          onClick={() => void wrap(DECLINE_ACTION, () => declineRequest(request.id))()}
        >
          Decline
        </button>
      )}
      {showCancel && (
        <button
          type="button"
          className="btn btn--secondary btn--sm"
          data-testid="cancel-button"
          disabled={busy}
          onClick={() => void wrap(CANCEL_ACTION, () => cancelRequest(request.id))()}
        >
          Cancel
        </button>
      )}
      <Link to={`/requests/${request.id}`} className="btn btn--secondary btn--sm">
        View Details
      </Link>
    </div>
  );
}

