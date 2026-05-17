type Props = {
  message: string;
};

export function ActionOverlay({ message }: Props) {
  return (
    <div
      className="action-overlay"
      data-testid="action-overlay"
      role="status"
      aria-live="polite"
      aria-busy="true"
    >
      <div className="action-overlay__panel">
        <span className="action-overlay__spinner" aria-hidden />
        <p className="action-overlay__message">{message}</p>
      </div>
    </div>
  );
}
