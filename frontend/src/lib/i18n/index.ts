import { translations } from "./translations";
export { translations };
export type { Locale, Translations } from "./translations";

const STORAGE_KEY = "honeyaegis-locale";

export function getLocale(): "en" | "es" | "de" | "fr" | "el" {
  if (typeof window === "undefined") return "en";
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored && ["en", "es", "de", "fr", "el"].includes(stored)) {
    return stored as "en" | "es" | "de" | "fr" | "el";
  }
  // Detect browser language
  const browser = navigator.language.slice(0, 2).toLowerCase();
  if (["en", "es", "de", "fr", "el"].includes(browser)) {
    return browser as "en" | "es" | "de" | "fr" | "el";
  }
  return "en";
}

export function setLocale(locale: "en" | "es" | "de" | "fr" | "el"): void {
  if (typeof window !== "undefined") {
    localStorage.setItem(STORAGE_KEY, locale);
  }
}

export function useTranslations() {
  const locale = getLocale();
  return translations[locale];
}
