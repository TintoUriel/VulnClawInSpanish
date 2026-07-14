import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { loadUiPreferences, subscribeUiPreferences, type UiPreferences } from "../utils/preferences";
import en from "./en.json";
import es from "./es.json";

type Lang = "es-ES" | "en-US";
type Translations = Record<string, string>;
export type TFunction = (key: string, params?: Record<string, string>, fallback?: string) => string;

const TRANSLATIONS: Record<Lang, Translations> = {
  "en-US": en as Translations,
  "es-ES": es as Translations,
};

/* ── Instancia global (para taskLabels y otro código fuera de React) ── */

let _currentLang: Lang = resolveInitialLang();
let _currentTranslations: Translations = TRANSLATIONS[_currentLang];

function resolveInitialLang(): Lang {
  try {
    const preferences = loadUiPreferences();
    return preferences.language === "es-ES" ? "es-ES" : "en-US";
  } catch {
    return "en-US";
  }
}

/**
 * Función de traducción global — puede llamarse fuera de componentes React.
 *   t("key")                -> texto traducido
 *   t("key", {a:"1"})       -> reemplaza el marcador {a}
 *   t("key", {}, "fallback") -> usa fallback si la clave no existe
 *
 * Cadena de respaldo: idioma actual → inglés → la clave misma (o fallback)
 */
export function t(key: string, params?: Record<string, string>, fallback?: string): string {
  let text = _currentTranslations[key];
  if (text === undefined) {
    text = TRANSLATIONS["en-US"][key];
  }
  if (text === undefined) {
    text = fallback ?? key;
  }
  if (params) {
    for (const [k, v] of Object.entries(params)) {
      text = text.replace(`{${k}}`, String(v));
    }
  }
  return text;
}

/* ── React Context ── */

interface I18nContextValue {
  lang: Lang;
  t: (key: string, params?: Record<string, string>, fallback?: string) => string;
}

const I18nContext = createContext<I18nContextValue>({
  lang: _currentLang,
  t,
});

/**
 * React Hook — los componentes usan `const { t, lang } = useT()` para obtener la función de traducción.
 * Provoca un nuevo renderizado automáticamente cuando cambia el idioma.
 */
export function useT(): I18nContextValue {
  return useContext(I18nContext);
}

/**
 * I18nProvider — envuelve a <App /> en main.tsx.
 * Escucha cambios en las preferencias y actualiza el Context y la instancia global cuando cambia el idioma.
 */
export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>(_currentLang);

  useEffect(() => {
    const unsubscribe = subscribeUiPreferences((preferences: UiPreferences) => {
      const nextLang: Lang = preferences.language === "es-ES" ? "es-ES" : "en-US";
      if (nextLang !== _currentLang) {
        _currentLang = nextLang;
        _currentTranslations = TRANSLATIONS[nextLang];
        setLang(nextLang);
      }
    });
    return unsubscribe;
  }, []);

  const value = useMemo<I18nContextValue>(() => {
    const tFn: TFunction = (key, params, fallback) => {
      let text = TRANSLATIONS[lang][key];
      if (text === undefined) text = TRANSLATIONS["en-US"][key];
      if (text === undefined) text = fallback ?? key;
      if (params) {
        for (const [k, v] of Object.entries(params)) text = text.replace(`{${k}}`, String(v));
      }
      return text;
    };
    return { lang, t: tFn };
  }, [lang]);

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}
