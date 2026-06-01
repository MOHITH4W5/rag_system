"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { AppHeader } from "@/components/AppHeader";
import { ChatPanel } from "@/components/ChatPanel";
import { SourcesPanel } from "@/components/SourcesPanel";
import { StudioPanel } from "@/components/StudioPanel";
import {
  clearStoredToken,
  askQuestion,
  deleteDocument,
  generateFlashcards,
  generateMindMap,
  generateQuiz,
  getEngine,
  getHealth,
  getMe,
  getStoredToken,
  ingestFile,
  listDocuments,
  login,
  setStoredToken,
  setEngine,
} from "@/lib/api";
import type { AuthUser, ChatMessage, DocumentItem, EngineMode, ThemeMode } from "@/lib/types";

const THEME_KEY = "second_brain_theme";

export default function Page() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [question, setQuestion] = useState("");
  const [engine, setEngineState] = useState<EngineMode>("langchain");
  const [llmConnected, setLlmConnected] = useState(false);
  const [useWeb, setUseWeb] = useState(true);
  const [busy, setBusy] = useState(false);
  const [uploadBusy, setUploadBusy] = useState(false);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [theme, setTheme] = useState<ThemeMode>("dark");
  const [engineLoading, setEngineLoading] = useState(false);
  const [toolBusy, setToolBusy] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"quiz" | "flashcards" | "mindmap">("quiz");
  const [quizItems, setQuizItems] = useState<Array<{ question: string; answer: string; options?: string[]; explanation?: string }>>([]);
  const [flashcards, setFlashcards] = useState<Array<{ front: string; back: string }>>([]);
  const [flowNodes, setFlowNodes] = useState<Array<{ id: string; label: string }>>([]);
  const [flowEdges, setFlowEdges] = useState<Array<{ source: string; target: string; label?: string }>>([]);
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [loginBusy, setLoginBusy] = useState(false);
  const [loginError, setLoginError] = useState("");
  const [username, setUsername] = useState("user1");
  const [password, setPassword] = useState("user123");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const latestTopic = useMemo(() => question.trim() || messages.at(-1)?.content || "Current uploaded sources", [question, messages]);

  useEffect(() => {
    const savedTheme = localStorage.getItem(THEME_KEY);
    const nextTheme = savedTheme === "light" ? "light" : "dark";
    setTheme(nextTheme);
    document.documentElement.setAttribute("data-theme", nextTheme);
  }, []);

  useEffect(() => {
    async function boot() {
      const token = getStoredToken();
      if (!token) {
        setAuthLoading(false);
        return;
      }
      try {
        const [health, me, engineData, docs] = await Promise.all([getHealth(), getMe(), getEngine(), listDocuments()]);
        setLlmConnected(health.llm_connected);
        setCurrentUser(me);
        setEngineState(engineData.engine);
        setDocuments(docs);
      } catch {
        clearStoredToken();
        setCurrentUser(null);
        setLlmConnected(false);
      } finally {
        setAuthLoading(false);
      }
    }
    void boot();
  }, []);

  async function refreshDocuments() {
    const docs = await listDocuments();
    setDocuments(docs);
  }

  async function setEngineMode(next: EngineMode) {
    if (next === engine || engineLoading) return;
    setEngineLoading(true);
    try {
      const result = await setEngine(next);
      setEngineState(result.engine);
    } finally {
      setEngineLoading(false);
    }
  }

  function toggleTheme() {
    const nextTheme: ThemeMode = theme === "dark" ? "light" : "dark";
    setTheme(nextTheme);
    localStorage.setItem(THEME_KEY, nextTheme);
    document.documentElement.setAttribute("data-theme", nextTheme);
  }

  async function handleUpload(file: File) {
    setUploadBusy(true);
    try {
      await ingestFile(file);
      await refreshDocuments();
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Uploaded "${file.name}" successfully and indexed it for retrieval.`,
          engine,
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Upload failed: ${(error as Error).message}`,
          engine,
        },
      ]);
    } finally {
      setUploadBusy(false);
    }
  }

  async function handleAsk() {
    const q = question.trim();
    if (!q || busy) return;

    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setQuestion("");
    setBusy(true);
    try {
      const data = await askQuestion({ question: q, top_k: useWeb ? 8 : 5, use_web: useWeb });
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer || "No response returned.",
          engine: data.engine_used || data.runtime_engine || engine,
          sources: data.sources,
          responseTimeMs: data.response_time_ms,
        },
      ]);
    } catch (error) {
      if ((error as Error).message.includes("token")) {
        clearStoredToken();
        setCurrentUser(null);
      }
      setMessages((prev) => [...prev, { role: "assistant", content: `Error: ${(error as Error).message}`, engine }]);
    } finally {
      setBusy(false);
    }
  }

  function startVoiceCapture() {
    const SpeechRecognition = (window as Window & { webkitSpeechRecognition?: any; SpeechRecognition?: any }).webkitSpeechRecognition ||
      (window as Window & { webkitSpeechRecognition?: any; SpeechRecognition?: any }).SpeechRecognition;

    if (!SpeechRecognition) {
      setMessages((prev) => [...prev, { role: "assistant", content: "Voice input is not supported in this browser.", engine }]);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.onresult = (event: any) => {
      setQuestion(event.results[0][0].transcript);
    };
    recognition.onerror = () => {
      setMessages((prev) => [...prev, { role: "assistant", content: "Voice capture failed, please try again.", engine }]);
    };
    recognition.start();
  }

  async function runTool(kind: "quiz" | "flashcards" | "mindmap") {
    if (toolBusy) return;
    setToolBusy(kind);
    try {
      if (kind === "quiz") {
        const data = await generateQuiz(latestTopic, 5);
        setQuizItems(data.questions || []);
      }
      if (kind === "flashcards") {
        const data = await generateFlashcards(latestTopic, 8);
        setFlashcards(data.flashcards || []);
      }
      if (kind === "mindmap") {
        const data = await generateMindMap(latestTopic, 12);
        setFlowNodes(data.nodes || []);
        setFlowEdges(data.edges || []);
      }
    } catch (error) {
      if ((error as Error).message.includes("token")) {
        clearStoredToken();
        setCurrentUser(null);
      }
      setMessages((prev) => [...prev, { role: "assistant", content: `${kind} failed: ${(error as Error).message}`, engine }]);
    } finally {
      setToolBusy(null);
    }
  }

  async function handleDeleteDocument(docId: number) {
    try {
      await deleteDocument(docId);
      await refreshDocuments();
    } catch (error) {
      const message = (error as Error).message || "Delete failed";
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: message.includes("Not allowed")
            ? "Only admin can delete global documents. Private documents can be deleted by their owner."
            : `Delete failed: ${message}`,
          engine,
        },
      ]);
    }
  }

  async function handleLogin() {
    if (!username.trim() || !password.trim() || loginBusy) return;
    setLoginBusy(true);
    setLoginError("");
    try {
      const result = await login(username.trim(), password);
      setStoredToken(result.access_token);
      const [health, me, engineData, docs] = await Promise.all([getHealth(), getMe(), getEngine(), listDocuments()]);
      setLlmConnected(health.llm_connected);
      setCurrentUser(me);
      setEngineState(engineData.engine);
      setDocuments(docs);
    } catch (error) {
      setLoginError((error as Error).message);
    } finally {
      setLoginBusy(false);
    }
  }

  function handleLogout() {
    clearStoredToken();
    setCurrentUser(null);
    setMessages([]);
    setDocuments([]);
  }

  if (authLoading) {
    return (
      <div className="min-h-screen grid place-items-center p-6">
        <div className="sb-panel w-full max-w-md text-center">
          <p className="text-sm text-[var(--text-secondary)]">Checking session...</p>
        </div>
      </div>
    );
  }

  if (!currentUser) {
    return (
      <div className="min-h-screen grid place-items-center p-6">
        <div className="sb-panel w-full max-w-md space-y-4">
          <div>
            <p className="sb-overline">Second Brain Login</p>
            <h1 className="text-2xl font-semibold text-[var(--text-primary)]">Multi-User Secure Access</h1>
            <p className="mt-1 text-sm text-[var(--text-secondary)]">
              Demo users: admin/admin123, user1/user123, user2/user123
            </p>
          </div>

          <input
            className="sb-input w-full"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            placeholder="Username"
          />
          <input
            className="sb-input w-full"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Password"
            onKeyDown={(event) => {
              if (event.key === "Enter") void handleLogin();
            }}
          />
          {loginError ? <p className="text-sm text-red-400">{loginError}</p> : null}
          <button type="button" className="sb-primary-btn w-full" disabled={loginBusy} onClick={() => void handleLogin()}>
            {loginBusy ? "Signing in..." : "Sign In"}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-4 md:p-6">
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (file) void handleUpload(file);
        }}
      />

      <div className="mx-auto grid w-full max-w-[1580px] gap-4">
        <AppHeader
          engine={engine}
          setEngineMode={setEngineMode}
          engineLoading={engineLoading}
          llmConnected={llmConnected}
          theme={theme}
          onToggleTheme={toggleTheme}
          useWeb={useWeb}
          onToggleWeb={() => setUseWeb((prev) => !prev)}
          currentUser={currentUser}
          onLogout={handleLogout}
        />

        <main className="grid gap-4 xl:grid-cols-[320px_minmax(0,1fr)_360px]">
          <SourcesPanel
            documents={documents}
            uploadBusy={uploadBusy}
            currentUserRole={currentUser.role}
            onUploadClick={() => fileInputRef.current?.click()}
            onDelete={(docId) => void handleDeleteDocument(docId)}
          />

          <ChatPanel
            messages={messages}
            question={question}
            setQuestion={setQuestion}
            onAsk={handleAsk}
            busy={busy}
            engine={engine}
            onVoice={startVoiceCapture}
          />

          <StudioPanel
            activeTab={activeTab}
            onTabChange={setActiveTab}
            onGenerateQuiz={() => void runTool("quiz")}
            onGenerateFlashcards={() => void runTool("flashcards")}
            onGenerateMindMap={() => void runTool("mindmap")}
            busyTool={toolBusy}
            quizItems={quizItems}
            flashcards={flashcards}
            flowNodes={flowNodes}
            flowEdges={flowEdges}
          />
        </main>
      </div>
    </div>
  );
}
