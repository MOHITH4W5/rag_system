import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import reportWebVitals from "./reportWebVitals";

const THEME_KEY = "rag_theme_preference";
const VALID_THEMES = new Set(["dark-premium", "light-glass"]);

try {
  const savedTheme = window.localStorage.getItem(THEME_KEY);
  const initialTheme = VALID_THEMES.has(savedTheme) ? savedTheme : "dark-premium";
  document.documentElement.setAttribute("data-theme", initialTheme);
} catch {
  document.documentElement.setAttribute("data-theme", "dark-premium");
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

reportWebVitals();
