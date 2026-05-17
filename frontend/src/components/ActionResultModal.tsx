type Props = {
  variant: "success" | "error";
  message: string;
  referenceCode?: string | null;
  onClose: () => void;
};

export function ActionResultModal({ variant, message, referenceCode, onClose }: Props) {
  const isSuccess = variant === "success";

  return (
    <div
      className="action-modal-backdrop"
      data-testid="action-result-modal"
      role="alertdialog"
      aria-modal="true"
      aria-labelledby="action-result-title"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        className={`action-modal action-modal--${variant}`}
        onClick={(e) => e.stopPropagation()}
      >
        <div
          className={`action-modal__icon action-modal__icon--${variant}`}
          aria-hidden
        >
          {isSuccess ? "✓" : "!"}
        </div>
        <h2 id="action-result-title" className="action-modal__title">
          {isSuccess ? "Success" : "Something went wrong"}
        </h2>
        <p className="action-modal__message" data-testid="action-result-message">
          {message}
        </p>
        {referenceCode && (
          <p className="action-modal__reference" data-testid="action-result-reference">
            Request ID: <code>{referenceCode}</code>
          </p>
        )}
        <button
          type="button"
          className={`btn ${isSuccess ? "btn--primary" : "btn--danger"}`}
          data-testid="action-result-ok"
          autoFocus
          onClick={onClose}
        >
          OK
        </button>
      </div>
    </div>
  );
}
