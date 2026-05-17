import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { ApiError } from "../api/client";
import { ActionOverlay } from "../components/ActionOverlay";
import { ActionResultModal } from "../components/ActionResultModal";

const MIN_ACTION_MS = 2000;

export type RequestActionConfig = {
  loadingMessage: string;
  successMessage: string;
};

export const PAY_ACTION: RequestActionConfig = {
  loadingMessage: "Paying",
  successMessage: "Payment successful",
};

export const DECLINE_ACTION: RequestActionConfig = {
  loadingMessage: "Declining",
  successMessage: "Request declined successfully",
};

export const CANCEL_ACTION: RequestActionConfig = {
  loadingMessage: "Cancelling",
  successMessage: "Request cancelled successfully",
};

type ModalState = {
  variant: "success" | "error";
  message: string;
  referenceCode?: string | null;
};

function referenceCodeFromResult<T>(result: T): string | undefined {
  if (result && typeof result === "object" && "reference_code" in result) {
    const code = (result as { reference_code?: string }).reference_code;
    return typeof code === "string" ? code : undefined;
  }
  return undefined;
}

type RequestActionContextValue = {
  runRequestAction: <T>(config: RequestActionConfig, action: () => Promise<T>) => Promise<T>;
  busy: boolean;
};

const RequestActionContext = createContext<RequestActionContextValue | null>(null);

export function RequestActionProvider({ children }: { children: ReactNode }) {
  const [overlayMessage, setOverlayMessage] = useState<string | null>(null);
  const [modal, setModal] = useState<ModalState | null>(null);
  const modalResolveRef = useRef<(() => void) | null>(null);

  const showModal = useCallback(
    (variant: ModalState["variant"], message: string, referenceCode?: string | null) => {
      return new Promise<void>((resolve) => {
        modalResolveRef.current = resolve;
        setModal({ variant, message, referenceCode });
      });
    },
    [],
  );

  const closeModal = useCallback(() => {
    setModal(null);
    modalResolveRef.current?.();
    modalResolveRef.current = null;
  }, []);

  const runRequestAction = useCallback(
    async <T,>(config: RequestActionConfig, action: () => Promise<T>): Promise<T> => {
      setOverlayMessage(config.loadingMessage);
      const started = Date.now();
      try {
        const result = await action();
        const remaining = Math.max(0, MIN_ACTION_MS - (Date.now() - started));
        if (remaining > 0) {
          await new Promise((resolve) => window.setTimeout(resolve, remaining));
        }
        setOverlayMessage(null);
        await showModal("success", config.successMessage, referenceCodeFromResult(result));
        return result;
      } catch (err) {
        setOverlayMessage(null);
        const message = err instanceof ApiError ? err.message : "Action failed.";
        await showModal("error", message, null);
        throw err;
      }
    },
    [showModal],
  );

  const value = useMemo(
    () => ({
      runRequestAction,
      busy: overlayMessage !== null || modal !== null,
    }),
    [runRequestAction, overlayMessage, modal],
  );

  return (
    <RequestActionContext.Provider value={value}>
      {children}
      {overlayMessage && <ActionOverlay message={overlayMessage} />}
      {modal && (
        <ActionResultModal
          variant={modal.variant}
          message={modal.message}
          referenceCode={modal.referenceCode}
          onClose={closeModal}
        />
      )}
    </RequestActionContext.Provider>
  );
}

export function useRequestAction(): RequestActionContextValue {
  const ctx = useContext(RequestActionContext);
  if (!ctx) {
    throw new Error("useRequestAction must be used within RequestActionProvider");
  }
  return ctx;
}
