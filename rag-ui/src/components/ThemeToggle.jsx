export default function ThemeToggle({ isDark, onToggle }) {
  return (
    <button
      type="button"
      className="theme-toggle skeuo-control"
      role="switch"
      aria-checked={!isDark}
      aria-label="Toggle theme"
      onClick={onToggle}
    >
      <span className="theme-toggle-track" aria-hidden="true">
        <span className={`theme-toggle-thumb ${isDark ? "is-dark" : "is-light"}`} />
      </span>
      <span className="theme-toggle-text">{isDark ? "Dark" : "Light"}</span>
    </button>
  );
}
