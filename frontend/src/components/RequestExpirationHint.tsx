import { formatExpirationSummary } from "../utils/expiration";

type Props = {
  expiresAt: string;
  status: string;
  isExpired: boolean;
};

export function RequestExpirationHint({ expiresAt, status, isExpired }: Props) {
  const summary = formatExpirationSummary(expiresAt, status, isExpired);
  if (!summary) return null;

  return (
    <span
      className={
        summary === "Expired" ? "request-expiration request-expiration--expired" : "request-expiration"
      }
    >
      {summary}
    </span>
  );
}
