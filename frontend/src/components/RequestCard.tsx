import type { PaymentRequestSummary } from "../api/client";
import { AmountDisplay } from "./AmountDisplay";
import { RequestActions } from "./RequestActions";
import { RequestExpirationHint } from "./RequestExpirationHint";
import { StatusBadge } from "./StatusBadge";
import { resolveDisplayStatus } from "../utils/expiration";

type Props = {
  request: PaymentRequestSummary;
  direction: "incoming" | "outgoing";
  onRequestUpdated?: () => void;
};

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function RequestCard({ request, direction, onRequestUpdated }: Props) {
  const counterpartyLabel = direction === "incoming" ? "From" : "To";
  const displayStatus = resolveDisplayStatus(request.status, request.is_expired);

  return (
    <article className="request-card hide-desktop">
      <div className="request-card__header">
        <AmountDisplay amountMinor={request.amount_minor} currency={request.currency} />
        <StatusBadge status={displayStatus} />
      </div>
      <p className="request-card__meta">
        <span className="request-card__label">{counterpartyLabel}</span> {request.counterparty_label}
      </p>
      {request.note && (
        <p className="request-card__meta">
          <span className="request-card__label">Note</span> {request.note}
        </p>
      )}
      <p className="request-card__meta request-card__date">{formatDate(request.created_at)}</p>
      <p className="request-card__meta">
        <RequestExpirationHint
          expiresAt={request.expires_at}
          status={request.status}
          isExpired={request.is_expired}
        />
      </p>
      <RequestActions
        request={request}
        direction={direction}
        onRequestUpdated={onRequestUpdated}
      />
    </article>
  );
}
