import { useEffect, useState } from "react";

type Props = {
  expiresAt: string;
  status: string;
};

function formatRemaining(ms: number): string {
  if (ms <= 0) return "Expired";
  const totalSeconds = Math.floor(ms / 1000);
  const days = Math.floor(totalSeconds / 86400);
  const hours = Math.floor((totalSeconds % 86400) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  if (days > 0) return `${days}d ${hours}h remaining`;
  if (hours > 0) return `${hours}h ${minutes}m remaining`;
  return `${minutes}m remaining`;
}

export function ExpirationCountdown({ expiresAt, status }: Props) {
  const [remainingLabel, setRemainingLabel] = useState(() =>
    formatRemaining(new Date(expiresAt).getTime() - Date.now()),
  );

  useEffect(() => {
    if (status !== "PENDING") return;

    const update = () => {
      setRemainingLabel(formatRemaining(new Date(expiresAt).getTime() - Date.now()));
    };
    update();
    const timer = window.setInterval(update, 30_000);
    return () => window.clearInterval(timer);
  }, [expiresAt, status]);

  if (status !== "PENDING") return null;

  return (
    <p className="expiration-countdown" style={{ margin: "0.5rem 0 0", color: "var(--muted)" }}>
      Expires: {new Date(expiresAt).toLocaleString()} · {remainingLabel}
    </p>
  );
}
