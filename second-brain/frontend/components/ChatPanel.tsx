"use client";

import { Mic, SendHorizonal } from "lucide-react";

import type { ChatMessage, EngineMode } from "@/lib/types";

type Props = {
  messages: ChatMessage[];
  question: string;
  setQuestion: (value: string) => void;
  onAsk: () => void;
  busy: boolean;
  engine: EngineMode;
  onVoice: () => void;
};

export function ChatPanel({ messages, question, setQuestion, onAsk, busy, engine, onVoice }: Props) {
  return (
    <section className="sb-panel min-h-[600px]">
      <div className="flex items-center justify-between">
        <h2 className="sb-section-title">Chat</h2>
        <span className="sb-badge">Active engine: {engine}</span>
      </div>

      <div className="mt-4 h-[470px] overflow-auto rounded-2xl border border-[var(--border-soft)] bg-[var(--surface-soft)] p-3">
        {messages.length === 0 ? (
          <div className="sb-empty h-full">
            <p className="font-medium text-[var(--text-primary)]">Ask your first grounded question</p>
            <p className="mt-1 text-xs text-[var(--text-secondary)]">
              Responses are generated from your uploaded sources and optional web context.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {messages.map((message, index) => (
              <article
                key={`${message.role}-${index}`}
                className={`max-w-[92%] rounded-2xl border p-3 ${
                  message.role === "user"
                    ? "ml-auto border-[var(--accent-strong)] bg-[var(--accent-strong)] text-white"
                    : "border-[var(--border-soft)] bg-[var(--surface-elevated)] text-[var(--text-primary)]"
                }`}
              >
                <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</p>
                {message.role === "assistant" && message.sources?.length ? (
                  <div className="mt-3 flex flex-wrap gap-1.5">
                    {message.sources.map((source, i) => (
                      <span key={`${source.filename}-${i}`} className="sb-chip">
                        {source.filename}
                      </span>
                    ))}
                  </div>
                ) : null}
                {message.role === "assistant" ? (
                  <p className="mt-2 text-[11px] opacity-75">
                    {message.engine ? `Engine: ${message.engine}` : ""}{" "}
                    {message.responseTimeMs ? `• ${message.responseTimeMs} ms` : ""}
                  </p>
                ) : null}
              </article>
            ))}
          </div>
        )}
      </div>

      <div className="mt-4 flex gap-2">
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask anything from your sources..."
          className="sb-input min-h-[60px] flex-1 resize-none"
          onKeyDown={(event) => {
            if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
              onAsk();
            }
          }}
        />
        <button type="button" className="sb-icon-btn" onClick={onVoice} aria-label="Voice input">
          <Mic size={17} />
        </button>
        <button type="button" className="sb-primary-btn" disabled={busy} onClick={onAsk}>
          <SendHorizonal size={16} />
          {busy ? "Thinking..." : "Ask"}
        </button>
      </div>
    </section>
  );
}
