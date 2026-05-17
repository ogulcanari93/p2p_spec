import type { PaymentRequestSummary } from "../api/client";
import { AmountDisplay } from "./AmountDisplay";
import { RequestActions } from "./RequestActions";
import { StatusBadge } from "./StatusBadge";

type Props = {
  request: PaymentRequestSummary;
  direction: "incoming" | "outgoing";
};

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function RequestCard({ request, direction }: Props) {
  const counterpartyLabel = direction === "incoming" ? "From" : "To";
  const displayStatus =
    request.is_expired && request.status === "PENDING" ? "EXPIRED" : request.status;

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
      <RequestActions request={request} direction={direction} />
    </article>
  );
}
