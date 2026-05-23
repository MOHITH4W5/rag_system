"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { AppHeader } from "@/components/AppHeader";
import { ChatPanel } from "@/components/ChatPanel";
import { SourcesPanel } from "@/components/SourcesPanel";
import { StudioPanel } from "@/components/StudioPanel";
import {
  askQuestion,
  deleteDocument,
  generateFlashcards,
  generateMindMap,
  generateQuiz,
  getEngine,
  getHealth,
  ingestFile,
  listDocuments,
  setEngine,
} from "@/lib/api";
import type { ChatMessage, DocumentItem, EngineMode, ThemeMode } from "@/lib/types";

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
      try {
        const [health, engineData, docs] = await Promise.all([getHealth(), getEngine(), listDocuments()]);
        setLlmConnected(health.llm_connected);
        setEngineState(engineData.engine);
        setDocuments(docs);
      } catch {
        setLlmConnected(false);
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
      setMessages((prev) => [...prev, { role: "assistant", content: `${kind} failed: ${(error as Error).message}`, engine }]);
    } finally {
      setToolBusy(null);
    }
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
        />

        <main className="grid gap-4 xl:grid-cols-[320px_minmax(0,1fr)_360px]">
          <SourcesPanel
            documents={documents}
            uploadBusy={uploadBusy}
            onUploadClick={() => fileInputRef.current?.click()}
            onDelete={async (docId) => {
              await deleteDocument(docId);
              await refreshDocuments();
            }}
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
