import type { RequestEvent } from "../api/client";

const EVENT_LABELS: Record<string, string> = {
  REQUEST_CREATED: "Request created",
  REQUEST_PAID: "Payment received",
  REQUEST_DECLINED: "Request declined",
  REQUEST_CANCELLED: "Request cancelled",
  REQUEST_EXPIRED: "Request expired",
};

type Props = {
  events: RequestEvent[];
};

export function EventHistory({ events }: Props) {
  if (events.length === 0) {
    return <p style={{ color: "var(--muted)" }}>No events yet.</p>;
  }

  return (
    <ul className="event-history" style={{ listStyle: "none", padding: 0, margin: 0 }}>
      {events.map((event) => (
        <li key={event.id} className="event-history__item">
          <strong>{EVENT_LABELS[event.event_type] ?? event.event_type}</strong>
          {event.previous_status && event.new_status && (
            <span style={{ color: "var(--muted)" }}>
              {" "}
              ({event.previous_status} → {event.new_status})
            </span>
          )}
          <div style={{ fontSize: "0.8125rem", color: "var(--muted)" }}>
            {new Date(event.created_at).toLocaleString()}
          </div>
        </li>
      ))}
    </ul>
  );
}
