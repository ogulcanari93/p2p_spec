export function resolveDisplayStatus(status: string, isExpired: boolean): string {
  if (status === "EXPIRED" || (isExpired && status === "PENDING")) {
    return "EXPIRED";
  }
  return status;
}

export function formatTimeRemaining(expiresAt: string): string {
  const ms = new Date(expiresAt).getTime() - Date.now();
  if (ms <= 0) return "Expired";

  const totalSeconds = Math.floor(ms / 1000);
  const days = Math.floor(totalSeconds / 86400);
  const hours = Math.floor((totalSeconds % 86400) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);

  if (days > 0) return `${days}d ${hours}h ${minutes}m left`;
  if (hours > 0) return `${hours}h ${minutes}m left`;
  return `${minutes}m left`;
}

export function formatExpirationSummary(
  expiresAt: string,
  status: string,
  isExpired: boolean,
): string {
  const display = resolveDisplayStatus(status, isExpired);
  if (display === "EXPIRED") return "Expired";
  if (status !== "PENDING") return "";
  return formatTimeRemaining(expiresAt);
}
