import type { ReactNode } from "react";

type Props = {
  title: string;
  description?: string;
  action?: ReactNode;
};

export function EmptyState({ title, description, action }: Props) {
  return (
    <div className="empty-state">
      <p style={{ margin: "0 0 0.5rem", fontWeight: 600, color: "var(--text)" }}>{title}</p>
      {description && <p style={{ margin: "0 0 1rem" }}>{description}</p>}
      {action}
    </div>
  );
}
