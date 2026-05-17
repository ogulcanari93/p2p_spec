type Props = {
  status: string;
};

export function StatusBadge({ status }: Props) {
  const key = status.toLowerCase();
  return <span className={`badge badge--${key}`}>{status}</span>;
}
