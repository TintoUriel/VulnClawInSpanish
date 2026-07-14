export interface UiPreferences {
  language: "es-ES" | "en-US";
  defaultCheckMode: "quick" | "standard" | "deep" | "continuous";
  reportFormat: "markdown" | "html";
  showTechnicalLogs: boolean;
  defaultBoundary: BoundaryDefaults;
}

export interface BoundaryDefaults {
  onlyPort: string;
  onlyHost: string;
  onlyPath: string;
  blockedHost: string;
  blockedPath: string;
  allowActions: string[];
  blockActions: string[];
}

const STORAGE_KEY = "vulnclaw.ui.preferences";
export const UI_PREFERENCES_EVENT = "vulnclaw.ui.preferences.updated";

export const DEFAULT_UI_PREFERENCES: UiPreferences = {
  language: "en-US",
  defaultCheckMode: "standard",
  reportFormat: "markdown",
  showTechnicalLogs: false,
  defaultBoundary: {
    onlyPort: "",
    onlyHost: "",
    onlyPath: "",
    blockedHost: "",
    blockedPath: "",
    allowActions: [],
    blockActions: [],
  },
};

export function loadUiPreferences(): UiPreferences {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return DEFAULT_UI_PREFERENCES;
    const parsed = JSON.parse(raw) as Partial<UiPreferences>;
    return {
      language: parsed.language === "es-ES" ? "es-ES" : "en-US",
      defaultCheckMode: isCheckMode(parsed.defaultCheckMode) ? parsed.defaultCheckMode : DEFAULT_UI_PREFERENCES.defaultCheckMode,
      reportFormat: parsed.reportFormat === "html" ? "html" : "markdown",
      showTechnicalLogs: Boolean(parsed.showTechnicalLogs),
      defaultBoundary: normalizeBoundaryDefaults(parsed.defaultBoundary),
    };
  } catch {
    return DEFAULT_UI_PREFERENCES;
  }
}

export function saveUiPreferences(preferences: UiPreferences): void {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences));
  window.dispatchEvent(new CustomEvent<UiPreferences>(UI_PREFERENCES_EVENT, { detail: preferences }));
}

export function subscribeUiPreferences(onChange: (preferences: UiPreferences) => void): () => void {
  const handleLocalUpdate = (event: Event) => {
    const customEvent = event as CustomEvent<UiPreferences>;
    onChange(customEvent.detail ?? loadUiPreferences());
  };
  const handleStorageUpdate = (event: StorageEvent) => {
    if (event.key === STORAGE_KEY) onChange(loadUiPreferences());
  };

  window.addEventListener(UI_PREFERENCES_EVENT, handleLocalUpdate);
  window.addEventListener("storage", handleStorageUpdate);

  return () => {
    window.removeEventListener(UI_PREFERENCES_EVENT, handleLocalUpdate);
    window.removeEventListener("storage", handleStorageUpdate);
  };
}

function isCheckMode(value: unknown): value is UiPreferences["defaultCheckMode"] {
  return value === "quick" || value === "standard" || value === "deep" || value === "continuous";
}

function normalizeBoundaryDefaults(value: unknown): BoundaryDefaults {
  const raw = value && typeof value === "object" ? value as Partial<BoundaryDefaults> : {};
  return {
    onlyPort: typeof raw.onlyPort === "string" ? raw.onlyPort : "",
    onlyHost: typeof raw.onlyHost === "string" ? raw.onlyHost : "",
    onlyPath: typeof raw.onlyPath === "string" ? raw.onlyPath : "",
    blockedHost: typeof raw.blockedHost === "string" ? raw.blockedHost : "",
    blockedPath: typeof raw.blockedPath === "string" ? raw.blockedPath : "",
    allowActions: Array.isArray(raw.allowActions) ? raw.allowActions.map(String) : [],
    blockActions: Array.isArray(raw.blockActions) ? raw.blockActions.map(String) : [],
  };
}
