import type { PaymentRequestSummary } from "../api/client";
import { AmountDisplay } from "./AmountDisplay";
import { RequestActions } from "./RequestActions";
import { StatusBadge } from "./StatusBadge";

type Props = {
  requests: PaymentRequestSummary[];
  direction: "incoming" | "outgoing";
};

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function RequestTable({ requests, direction }: Props) {
  const counterpartyHeader = direction === "incoming" ? "From" : "To";

  return (
    <div className="table-wrap hide-mobile">
      <table className="requests-table">
        <thead>
          <tr>
            <th>{counterpartyHeader}</th>
            <th>Amount</th>
            <th>Status</th>
            <th>Note</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {requests.map((r) => (
            <tr key={r.id}>
              <td>{r.counterparty_label}</td>
              <td>
                <AmountDisplay amountMinor={r.amount_minor} currency={r.currency} />
              </td>
              <td>
                <StatusBadge status={r.is_expired && r.status === "PENDING" ? "EXPIRED" : r.status} />
              </td>
              <td className="requests-table__note">{r.note ?? "—"}</td>
              <td>{formatDate(r.created_at)}</td>
              <td>
                <RequestActions request={r} direction={direction} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
