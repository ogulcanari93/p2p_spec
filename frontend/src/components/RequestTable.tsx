import type { PaymentRequestSummary } from "../api/client";
import { AmountDisplay } from "./AmountDisplay";
import { RequestActions } from "./RequestActions";
import { RequestExpirationHint } from "./RequestExpirationHint";
import { StatusBadge } from "./StatusBadge";
import { resolveDisplayStatus } from "../utils/expiration";

type Props = {
  requests: PaymentRequestSummary[];
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

export function RequestTable({ requests, direction, onRequestUpdated }: Props) {
  const counterpartyHeader = direction === "incoming" ? "From" : "To";

  return (
    <div className="table-wrap hide-mobile">
      <table className="requests-table">
        <thead>
          <tr>
            <th>Request ID</th>
            <th>{counterpartyHeader}</th>
            <th>Amount</th>
            <th>Status</th>
            <th>Note</th>
            <th>Created</th>
            <th>Expiration</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {requests.map((r) => (
            <tr key={r.id}>
              <td>
                <code className="reference-code__value reference-code__value--compact">
                  {r.reference_code}
                </code>
              </td>
              <td>{r.counterparty_label}</td>
              <td>
                <AmountDisplay amountMinor={r.amount_minor} currency={r.currency} />
              </td>
              <td>
                <StatusBadge status={resolveDisplayStatus(r.status, r.is_expired)} />
              </td>
              <td className="requests-table__note">{r.note ?? "—"}</td>
              <td>{formatDate(r.created_at)}</td>
              <td>
                <RequestExpirationHint
                  expiresAt={r.expires_at}
                  status={r.status}
                  isExpired={r.is_expired}
                />
              </td>
              <td>
                <RequestActions
                  request={r}
                  direction={direction}
                  onRequestUpdated={onRequestUpdated}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
