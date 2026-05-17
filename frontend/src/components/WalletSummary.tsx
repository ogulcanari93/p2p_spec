import { useEffect, useState } from "react";
import { ApiError, fetchWallet, type Wallet } from "../api/client";
import { AmountDisplay } from "./AmountDisplay";

type Props = {
  refreshKey?: number;
};

export function WalletSummary({ refreshKey = 0 }: Props) {
  const [wallet, setWallet] = useState<Wallet | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchWallet()
      .then(setWallet)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load wallet"));
  }, [refreshKey]);

  if (error) {
    return (
      <div className="card wallet-summary">
        <p className="form-error">{error}</p>
      </div>
    );
  }

  if (!wallet) {
    return (
      <div className="card wallet-summary">
        <p style={{ color: "var(--muted)", margin: 0 }}>Loading wallet…</p>
      </div>
    );
  }

  return (
    <div className="card wallet-summary">
      <h2 style={{ marginTop: 0, fontSize: "1rem" }}>Your wallet</h2>
      <p style={{ margin: 0, fontSize: "1.5rem" }}>
        <AmountDisplay amountMinor={wallet.balance_minor} currency={wallet.currency} />
      </p>
      <p style={{ margin: "0.25rem 0 0", color: "var(--muted)", fontSize: "0.875rem" }}>
        {wallet.display_name ?? `${wallet.currency} internal wallet`} · {wallet.status}
      </p>
    </div>
  );
}
