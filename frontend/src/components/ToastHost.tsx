import { useT } from "../i18n";

export type ToastTone = "success" | "error" | "info";

export interface ToastItem {
  id: number;
  tone: ToastTone;
  title: string;
  copy?: string;
  actionLabel?: string;
  onAction?: () => void;
}

interface ToastHostProps {
  toasts: ToastItem[];
  onDismiss: (id: number) => void;
}

export function ToastHost({ toasts, onDismiss }: ToastHostProps) {
  const { t } = useT();
  if (!toasts.length) return null;

  return (
    <div className="toast-host" aria-live="polite" aria-relevant="additions removals">
      {toasts.map((toast) => (
        <article key={toast.id} className={`toast toast-${toast.tone}`}>
          <div>
            <strong>{toast.title}</strong>
            {toast.copy && <p>{toast.copy}</p>}
            {toast.actionLabel && toast.onAction && (
              <button
                type="button"
                className="toast-action-btn"
                onClick={() => {
                  toast.onAction?.();
                  onDismiss(toast.id);
                }}
              >
                {toast.actionLabel}
              </button>
            )}
          </div>
          <button type="button" className="toast-close-btn" aria-label={t("toast.close_notification")} onClick={() => onDismiss(toast.id)}>
            x
          </button>
        </article>
      ))}
    </div>
  );
}
