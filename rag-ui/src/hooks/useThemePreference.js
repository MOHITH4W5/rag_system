import { useEffect, useMemo, useState } from "react";

export const THEME_KEY = "rag_theme_preference";
export const THEMES = {
  DARK: "dark-premium",
  LIGHT: "light-glass",
};

function getStoredTheme() {
  if (typeof window === "undefined") {
    return THEMES.DARK;
  }

  const savedTheme = window.localStorage.getItem(THEME_KEY);
  if (savedTheme === THEMES.DARK || savedTheme === THEMES.LIGHT) {
    return savedTheme;
  }

  return THEMES.DARK;
}

export function applyTheme(theme) {
  if (typeof document === "undefined") {
    return;
  }
  document.documentElement.setAttribute("data-theme", theme);
}

export default function useThemePreference() {
  const [theme, setTheme] = useState(getStoredTheme);

  useEffect(() => {
    applyTheme(theme);
    window.localStorage.setItem(THEME_KEY, theme);
  }, [theme]);

  const isDark = useMemo(() => theme === THEMES.DARK, [theme]);

  return {
    theme,
    isDark,
    setTheme,
    toggleTheme: () => setTheme((current) => (current === THEMES.DARK ? THEMES.LIGHT : THEMES.DARK)),
  };
}
