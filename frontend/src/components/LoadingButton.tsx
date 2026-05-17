import { useState, type ButtonHTMLAttributes, type ReactNode } from "react";

type Props = Omit<ButtonHTMLAttributes<HTMLButtonElement>, "onClick" | "children"> & {
  onClick: () => Promise<void>;
  children: ReactNode;
  loadingLabel?: string;
  minDurationMs?: number;
};

export function LoadingButton({
  onClick,
  children,
  loadingLabel = "Processing…",
  minDurationMs = 2500,
  className = "",
  disabled,
  ...rest
}: Props) {
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    if (loading || disabled) return;
    setLoading(true);
    const started = Date.now();
    try {
      await onClick();
    } finally {
      const remaining = Math.max(0, minDurationMs - (Date.now() - started));
      if (remaining > 0) {
        await new Promise((resolve) => window.setTimeout(resolve, remaining));
      }
      setLoading(false);
    }
  };

  return (
    <button
      type="button"
      {...rest}
      className={`${className}${loading ? " btn--loading" : ""}`.trim()}
      disabled={disabled || loading}
      onClick={() => void handleClick()}
      aria-busy={loading}
    >
      {loading ? (
        <span className="btn__loading">
          <span className="btn__spinner" aria-hidden />
          {loadingLabel}
        </span>
      ) : (
        children
      )}
    </button>
  );
}
