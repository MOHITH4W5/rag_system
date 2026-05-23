import ThemeToggle from "./ThemeToggle";

const QUICK_PROMPTS = [
  "Give me an executive summary",
  "List the most important points",
  "What are the database entities?",
  "Explain this like a project interviewer",
];

function EngineSwitch({ engineMode, loading, onSwitch }) {
  return (
    <div className="engine-switch" role="tablist" aria-label="RAG engine selector">
      {[
        { id: "langchain", label: "LangChain" },
        { id: "classic", label: "Classic" },
      ].map((engine) => (
        <button
          key={engine.id}
          type="button"
          className={`engine-btn ${engineMode === engine.id ? "active" : ""}`}
          disabled={loading}
          onClick={() => onSwitch(engine.id)}
        >
          {engine.label}
        </button>
      ))}
    </div>
  );
}

function EmptyState({ onPrompt }) {
  return (
    <section className="empty-state panel">
      <p className="eyebrow">Intelligent Document Workspace</p>
      <h1>Turn static documents into searchable, explainable insights.</h1>
      <p className="empty-note">
        Upload your documents, run semantic retrieval, and generate grounded answers with clear source traceability.
      </p>
      <div className="prompt-grid">
        {QUICK_PROMPTS.map((prompt) => (
          <button key={prompt} type="button" className="prompt-chip skeuo-control" onClick={() => onPrompt(prompt)}>
            {prompt}
          </button>
        ))}
      </div>
    </section>
  );
}

function MessageRow({ message }) {
  const isUser = message.role === "user";

  return (
    <article className={`message-row ${isUser ? "user" : "assistant"}`}>
      <div className="message-label">{isUser ? "You" : "Assistant"}</div>
      <div className={`message-bubble ${isUser ? "user" : "assistant"}`}>
        <p>{message.content}</p>
      </div>
      {!isUser && (message.sources?.length > 0 || message.time || message.engineUsed) && (
        <div className="message-meta">
          {message.sources?.map((source, idx) => (
            <span key={`${source.filename}-${idx}`} className="source-pill">
              {source.filename}
            </span>
          ))}
          {message.time ? <span className="time-pill">{message.time} ms</span> : null}
          {message.engineUsed ? <span className="engine-pill">{message.engineUsed}</span> : null}
        </div>
      )}
    </article>
  );
}

function TypingState() {
  return (
    <div className="typing-row" aria-live="polite" aria-label="Assistant is generating a response">
      <span className="typing-dot" />
      <span className="typing-dot" />
      <span className="typing-dot" />
    </div>
  );
}

function Composer({ input, loading, onInputChange, onKeyDown, onSubmit, textareaRef }) {
  return (
    <section className="composer panel">
      <label className="sr-only" htmlFor="question-input">
        Ask a question
      </label>
      <textarea
        id="question-input"
        ref={textareaRef}
        rows={1}
        value={input}
        placeholder="Ask anything about your uploaded documents..."
        onChange={onInputChange}
        onKeyDown={onKeyDown}
      />
      <button type="button" className="send-btn skeuo-control" onClick={onSubmit} disabled={!input.trim() || loading}>
        {loading ? "Thinking..." : "Send"}
      </button>
    </section>
  );
}

export default function ChatPanel({
  docsCount,
  llmConnected,
  messages,
  loading,
  input,
  isDark,
  apiBase,
  engineMode,
  engineSwitchLoading,
  engineSwitchError,
  sidebarOpen,
  onToggleSidebar,
  onToggleTheme,
  onSwitchEngine,
  onPrompt,
  onInputChange,
  onKeyDown,
  onSubmit,
  textareaRef,
  bottomRef,
}) {
  return (
    <div className="chat-panel">
      <header className="topbar panel">
        <div className="topbar-left">
          <button
            type="button"
            className="mobile-menu-btn skeuo-control"
            onClick={onToggleSidebar}
            aria-label={sidebarOpen ? "Close sidebar" : "Open sidebar"}
          >
            {sidebarOpen ? "Close" : "Menu"}
          </button>
          <div>
            <p className="eyebrow">SaaS Dashboard</p>
            <h2>{docsCount > 0 ? `${docsCount} documents indexed` : "No documents indexed"}</h2>
            <div className="kpi-row" role="status" aria-live="polite">
              <span className={`kpi-chip ${llmConnected ? "ok" : "warn"}`}>{llmConnected ? "LLM online" : "LLM offline"}</span>
              <span className="kpi-chip">Engine: {engineMode}</span>
              <span className="kpi-chip">API: {apiBase}</span>
            </div>
            {engineSwitchError ? <p className="engine-error">{engineSwitchError}</p> : null}
          </div>
        </div>

        <div className="topbar-controls">
          <EngineSwitch engineMode={engineMode} loading={engineSwitchLoading} onSwitch={onSwitchEngine} />
          <ThemeToggle isDark={isDark} onToggle={onToggleTheme} />
        </div>
      </header>

      <main className="conversation panel" role="log" aria-live="polite">
        {messages.length === 0 ? (
          <EmptyState onPrompt={onPrompt} />
        ) : (
          <>
            {messages.map((message, idx) => (
              <MessageRow key={`${message.role}-${idx}`} message={message} />
            ))}
            {loading && <TypingState />}
          </>
        )}
        <div ref={bottomRef} />
      </main>

      <Composer
        input={input}
        loading={loading}
        onInputChange={onInputChange}
        onKeyDown={onKeyDown}
        onSubmit={onSubmit}
        textareaRef={textareaRef}
      />
    </div>
  );
}
