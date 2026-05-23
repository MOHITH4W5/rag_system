import { useEffect, useRef, useState } from "react";
import ChatPanel from "./components/ChatPanel";
import SidebarPanel from "./components/SidebarPanel";
import useThemePreference from "./hooks/useThemePreference";
import "./App.css";

const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8000";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [docs, setDocs] = useState([]);
  const [llmConnected, setLlmConnected] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [statusMsg, setStatusMsg] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [engineMode, setEngineMode] = useState("langchain");
  const [engineSwitchLoading, setEngineSwitchLoading] = useState(false);
  const [engineSwitchError, setEngineSwitchError] = useState("");

  const bottomRef = useRef(null);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);

  const { isDark, toggleTheme } = useThemePreference();

  useEffect(() => {
    checkHealth();
    fetchDocs();
    fetchEngineMode();
  }, []);

  useEffect(() => {
    if (bottomRef.current && typeof bottomRef.current.scrollIntoView === "function") {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, loading]);

  const checkHealth = async () => {
    try {
      const response = await fetch(`${API_BASE}/health`);
      const data = await response.json();
      setLlmConnected(Boolean(data.llm_connected));
      if (data.rag_engine) {
        setEngineMode(data.rag_engine);
      }
    } catch {
      setLlmConnected(false);
    }
  };

  const fetchEngineMode = async () => {
    try {
      const response = await fetch(`${API_BASE}/engine`);
      const data = await response.json();
      if (data.engine) {
        setEngineMode(data.engine);
      }
    } catch {
      // keep current mode
    }
  };

  const switchEngineMode = async (nextMode) => {
    if (nextMode === engineMode || engineSwitchLoading) {
      return;
    }

    setEngineSwitchLoading(true);
    setEngineSwitchError("");

    try {
      const response = await fetch(`${API_BASE}/engine`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ engine: nextMode }),
      });

      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || "Failed to switch engine");
      }

      const data = await response.json();
      if (data.engine) {
        setEngineMode(data.engine);
      }
    } catch (error) {
      setEngineSwitchError(error.message || "Failed to switch engine");
      setTimeout(() => setEngineSwitchError(""), 4200);
    } finally {
      setEngineSwitchLoading(false);
    }
  };

  const fetchDocs = async () => {
    try {
      const response = await fetch(`${API_BASE}/documents`);
      const data = await response.json();
      setDocs(Array.isArray(data) ? data : []);
    } catch {
      setDocs([]);
    }
  };

  const handleUpload = async (file) => {
    if (!file) {
      return;
    }

    setUploading(true);
    setStatusMsg({ text: `Processing ${file.name}...`, type: "info" });

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_BASE}/upload`, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();

      if (data.success) {
        setStatusMsg({ text: `${data.chunks_processed} chunks indexed successfully.`, type: "ok" });
        await fetchDocs();
      } else {
        setStatusMsg({ text: `Upload failed: ${data.detail || "Unknown error"}`, type: "err" });
      }
    } catch (error) {
      setStatusMsg({ text: `Upload failed: ${error.message}`, type: "err" });
    } finally {
      setUploading(false);
      setTimeout(() => setStatusMsg(null), 4200);
    }
  };

  const handleDelete = async (id) => {
    try {
      await fetch(`${API_BASE}/documents/${id}`, { method: "DELETE" });
      await fetchDocs();
    } catch (error) {
      setStatusMsg({ text: `Delete failed: ${error.message}`, type: "err" });
      setTimeout(() => setStatusMsg(null), 4200);
    }
  };

  const ask = async (quickPrompt) => {
    const question = quickPrompt || input.trim();
    if (!question || loading) {
      return;
    }

    setInput("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "32px";
    }

    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer || data.detail || "No response returned.",
          sources: data.sources || [],
          time: data.response_time_ms,
          engineUsed: data.engine_used || engineMode,
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Request failed: ${error.message}`,
          sources: [],
          engineUsed: engineMode,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (event) => {
    setInput(event.target.value);
    event.target.style.height = "32px";
    event.target.style.height = `${Math.min(event.target.scrollHeight, 160)}px`;
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      ask();
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragging(false);
    handleUpload(event.dataTransfer.files?.[0]);
  };

  const handleFileChange = (event) => {
    handleUpload(event.target.files?.[0]);
    event.target.value = "";
  };

  return (
    <div className="app-shell">
      <div className={`sidebar-backdrop ${sidebarOpen ? "visible" : ""}`} aria-hidden="true" onClick={() => setSidebarOpen(false)} />

      <aside className={`sidebar-panel ${sidebarOpen ? "open" : ""}`}>
        <SidebarPanel
          llmConnected={llmConnected}
          dragging={dragging}
          uploading={uploading}
          statusMsg={statusMsg}
          docs={docs}
          fileInputRef={fileInputRef}
          onDrop={handleDrop}
          onDragOver={(event) => {
            event.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onFileChange={handleFileChange}
          onDelete={handleDelete}
        />
      </aside>

      <ChatPanel
        docsCount={docs.length}
        llmConnected={llmConnected}
        messages={messages}
        loading={loading}
        input={input}
        isDark={isDark}
        apiBase={API_BASE}
        engineMode={engineMode}
        engineSwitchLoading={engineSwitchLoading}
        engineSwitchError={engineSwitchError}
        sidebarOpen={sidebarOpen}
        onToggleSidebar={() => setSidebarOpen((prev) => !prev)}
        onToggleTheme={toggleTheme}
        onSwitchEngine={switchEngineMode}
        onPrompt={ask}
        onInputChange={handleInputChange}
        onKeyDown={handleKeyDown}
        onSubmit={() => ask()}
        textareaRef={textareaRef}
        bottomRef={bottomRef}
      />
    </div>
  );
}
