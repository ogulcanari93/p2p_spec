import { useEffect, useState } from "react";
import { ApiError, fetchDestinations, type PaymentDestination } from "../api/client";

type Props = {
  currency: string;
  value: string;
  onChange: (destinationId: string) => void;
};

export function DestinationSelector({ currency, value, onChange }: Props) {
  const [destinations, setDestinations] = useState<PaymentDestination[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetchDestinations()
      .then((list) => {
        if (cancelled) return;
        const filtered = list.filter((d) => d.currency === currency);
        setDestinations(filtered);
        const def = filtered.find((d) => d.is_default) ?? filtered[0];
        if (def && !value) onChange(def.id);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof ApiError ? err.message : "Failed to load destinations");
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps -- set default once when destinations load
  }, [currency]);

  if (loading) return <p style={{ color: "var(--muted)" }}>Loading destinations…</p>;
  if (error) return <p className="form-error">{error}</p>;
  if (destinations.length === 0) {
    return <p className="form-error">No active destination for {currency}.</p>;
  }

  return (
    <div className="form-field">
      <label htmlFor="destination">Payment destination</label>
      <select
        id="destination"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        {destinations.map((d) => (
          <option key={d.id} value={d.id}>
            {d.display_label}
            {d.masked_identifier ? ` (${d.masked_identifier})` : ""}
            {d.is_default ? " — default" : ""}
          </option>
        ))}
      </select>
    </div>
  );
}
