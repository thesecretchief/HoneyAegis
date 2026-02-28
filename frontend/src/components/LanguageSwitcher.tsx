"use client";

import { useState, useEffect } from "react";
import { getLocale, setLocale, type Locale } from "@/lib/i18n";

const LANGUAGES: { value: Locale; label: string; flag: string }[] = [
  { value: "en", label: "English", flag: "EN" },
  { value: "es", label: "Espanol", flag: "ES" },
  { value: "de", label: "Deutsch", flag: "DE" },
  { value: "fr", label: "Francais", flag: "FR" },
  { value: "el", label: "Ελληνικά", flag: "EL" },
];

export default function LanguageSwitcher() {
  const [current, setCurrent] = useState<Locale>("en");
  const [open, setOpen] = useState(false);

  useEffect(() => {
    setCurrent(getLocale());
  }, []);

  function handleSelect(locale: Locale) {
    setLocale(locale);
    setCurrent(locale);
    setOpen(false);
    window.location.reload();
  }

  const currentLang = LANGUAGES.find((l) => l.value === current);

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1 px-2 py-1 text-xs text-gray-500 hover:text-gray-300 transition-colors rounded"
        aria-label="Change language"
      >
        <span>{currentLang?.flag || "EN"}</span>
        <svg
          className="w-3 h-3"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>
      {open && (
        <div className="absolute bottom-full left-0 mb-1 bg-gray-800 border border-gray-700 rounded-lg shadow-lg py-1 z-50">
          {LANGUAGES.map((lang) => (
            <button
              key={lang.value}
              onClick={() => handleSelect(lang.value)}
              className={`block w-full text-left px-3 py-1.5 text-xs transition-colors ${
                current === lang.value
                  ? "text-honeyaegis-400 bg-gray-700/50"
                  : "text-gray-400 hover:text-gray-200 hover:bg-gray-700/30"
              }`}
            >
              {lang.flag} {lang.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
