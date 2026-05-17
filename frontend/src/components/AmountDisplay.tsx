type Props = {
  amountMinor: number;
  currency?: string;
};

export function AmountDisplay({ amountMinor, currency = "TRY" }: Props) {
  const major = currency === "TRY" ? (amountMinor / 100).toFixed(2) : String(amountMinor);
  return (
    <span className="amount">
      {major} {currency}
    </span>
  );
}
