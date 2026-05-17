export const STATUS_OPTIONS = [
  { value: "all", label: "All" },
  { value: "pending", label: "Pending" },
  { value: "paid", label: "Paid" },
  { value: "declined", label: "Declined" },
  { value: "expired", label: "Expired" },
  { value: "cancelled", label: "Cancelled" },
] as const;

type Props = {
  status: string;
  search: string;
  onStatusChange: (status: string) => void;
  onSearchChange: (search: string) => void;
};

export function SearchAndFilterBar({ status, search, onStatusChange, onSearchChange }: Props) {
  return (
    <div className="search-filter card">
      <div className="search-filter__row">
        <div className="form-field search-filter__field">
          <label htmlFor="status-filter">Status</label>
          <select
            id="status-filter"
            data-testid="status-filter"
            value={status}
            onChange={(e) => onStatusChange(e.target.value)}
          >
            {STATUS_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
        <div className="form-field search-filter__field search-filter__field--grow">
          <label htmlFor="request-search">Search</label>
          <input
            id="request-search"
            data-testid="request-search"
            type="search"
            placeholder="Sender, recipient, or note…"
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
          />
        </div>
      </div>
    </div>
  );
}

