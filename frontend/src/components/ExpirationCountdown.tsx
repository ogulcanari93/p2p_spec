import { useEffect, useState } from "react";
import { formatTimeRemaining } from "../utils/expiration";

type Props = {
  expiresAt: string;
  status: string;
  isExpired?: boolean;
};

export function ExpirationCountdown({ expiresAt, status, isExpired = false }: Props) {
  const showExpired = status === "EXPIRED" || isExpired;

  const [remainingLabel, setRemainingLabel] = useState(() =>
    showExpired ? "Expired" : formatTimeRemaining(expiresAt),
  );

  useEffect(() => {
    if (showExpired) {
      setRemainingLabel("Expired");
      return;
    }
    if (status !== "PENDING") return;

    const update = () => setRemainingLabel(formatTimeRemaining(expiresAt));
    update();
    const timer = window.setInterval(update, 60_000);
    return () => window.clearInterval(timer);
  }, [expiresAt, status, showExpired]);

  if (status !== "PENDING" && !showExpired) return null;

  if (showExpired) {
    return (
      <p className="expiration-countdown expiration-countdown--expired">
        This request has expired.
      </p>
    );
  }

  return (
    <p className="expiration-countdown">
      Expires {new Date(expiresAt).toLocaleString()} · <strong>{remainingLabel}</strong>
    </p>
  );
}
