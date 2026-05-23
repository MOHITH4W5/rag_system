"use client";

import { CircleDot, Cpu, MoonStar, Sparkles, Sun } from "lucide-react";

import type { EngineMode, ThemeMode } from "@/lib/types";

type Props = {
  engine: EngineMode;
  setEngineMode: (engine: EngineMode) => void;
  engineLoading: boolean;
  llmConnected: boolean;
  theme: ThemeMode;
  onToggleTheme: () => void;
  useWeb: boolean;
  onToggleWeb: () => void;
};

export function AppHeader({
  engine,
  setEngineMode,
  engineLoading,
  llmConnected,
  theme,
  onToggleTheme,
  useWeb,
  onToggleWeb,
}: Props) {
  return (
    <header className="sb-panel sb-header">
      <div className="flex flex-col gap-2">
        <p className="sb-overline">Second Brain</p>
        <h1 className="text-2xl font-semibold tracking-tight text-[var(--text-primary)] md:text-3xl">
          Research Workspace
        </h1>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <button
          type="button"
          onClick={() => setEngineMode("langchain")}
          disabled={engineLoading}
          className={`sb-pill ${engine === "langchain" ? "sb-pill-active" : ""}`}
          aria-label="Switch to LangChain engine"
        >
          <Cpu size={14} />
          LangChain
        </button>
        <button
          type="button"
          onClick={() => setEngineMode("classic")}
          disabled={engineLoading}
          className={`sb-pill ${engine === "classic" ? "sb-pill-active" : ""}`}
          aria-label="Switch to Classic engine"
        >
          <Sparkles size={14} />
          Classic
        </button>
        <button
          type="button"
          onClick={onToggleWeb}
          className={`sb-pill ${useWeb ? "sb-pill-active" : ""}`}
          aria-label="Toggle web-augmented retrieval"
        >
          <CircleDot size={14} />
          {useWeb ? "Web+Docs" : "Docs Only"}
        </button>
        <button type="button" onClick={onToggleTheme} className="sb-icon-btn" aria-label="Toggle theme">
          {theme === "dark" ? <Sun size={16} /> : <MoonStar size={16} />}
        </button>
      </div>

      <div className="col-span-full flex flex-wrap gap-2 pt-1 text-xs">
        <span className={`sb-badge ${llmConnected ? "sb-badge-ok" : "sb-badge-warn"}`}>
          Ollama: {llmConnected ? "Connected" : "Not Connected"}
        </span>
        <span className="sb-badge">API: localhost:8001</span>
        <span className="sb-badge">UI: localhost:3001</span>
        <span className="sb-badge">Engine: {engine}</span>
      </div>
    </header>
  );
}
