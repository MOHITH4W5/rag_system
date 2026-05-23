"use client";

import { BrainCircuit, LayoutPanelTop, Link, ListChecks } from "lucide-react";
import ReactFlow, { Background, Controls, MiniMap } from "reactflow";
import "reactflow/dist/style.css";

type QuizItem = { question: string; answer: string; options?: string[]; explanation?: string };
type FlashcardItem = { front: string; back: string };

type Props = {
  activeTab: "quiz" | "flashcards" | "mindmap";
  onTabChange: (tab: "quiz" | "flashcards" | "mindmap") => void;
  onGenerateQuiz: () => void;
  onGenerateFlashcards: () => void;
  onGenerateMindMap: () => void;
  busyTool: string | null;
  quizItems: QuizItem[];
  flashcards: FlashcardItem[];
  flowNodes: Array<{ id: string; label: string }>;
  flowEdges: Array<{ source: string; target: string; label?: string }>;
};

const tabs = [
  { key: "quiz", label: "Quiz", icon: ListChecks },
  { key: "flashcards", label: "Flashcards", icon: BrainCircuit },
  { key: "mindmap", label: "Mind Map", icon: Link },
] as const;

export function StudioPanel({
  activeTab,
  onTabChange,
  onGenerateQuiz,
  onGenerateFlashcards,
  onGenerateMindMap,
  busyTool,
  quizItems,
  flashcards,
  flowNodes,
  flowEdges,
}: Props) {
  const rfNodes = flowNodes.map((node, index) => ({
    id: node.id,
    position: { x: (index % 3) * 190, y: Math.floor(index / 3) * 130 },
    data: { label: node.label },
    style: {
      borderRadius: 16,
      border: "1px solid var(--border-soft)",
      background: "var(--surface-elevated)",
      color: "var(--text-primary)",
      padding: 10,
      width: 170,
      fontSize: 12,
    },
  }));

  const rfEdges = flowEdges.map((edge, index) => ({
    id: `${edge.source}-${edge.target}-${index}`,
    source: edge.source,
    target: edge.target,
    label: edge.label,
    style: { stroke: "var(--accent)" },
    labelStyle: { fill: "var(--text-secondary)", fontSize: 11 },
  }));

  return (
    <aside className="sb-panel min-h-[600px]">
      <div className="flex items-center justify-between">
        <h2 className="sb-section-title">Studio</h2>
        <span className="sb-badge">
          <LayoutPanelTop size={12} />
          Active tools
        </span>
      </div>

      <div className="mt-4 flex gap-1 rounded-xl border border-[var(--border-soft)] bg-[var(--surface-soft)] p-1">
        {tabs.map(({ key, label, icon: Icon }) => (
          <button
            type="button"
            key={key}
            onClick={() => onTabChange(key)}
            className={`flex flex-1 items-center justify-center gap-1.5 rounded-lg px-2 py-2 text-xs font-medium ${
              activeTab === key ? "bg-[var(--surface-elevated)] text-[var(--text-primary)] shadow" : "text-[var(--text-secondary)]"
            }`}
          >
            <Icon size={13} />
            {label}
          </button>
        ))}
      </div>

      <div className="mt-3">
        {activeTab === "quiz" ? (
          <>
            <button type="button" className="sb-secondary-btn w-full" onClick={onGenerateQuiz} disabled={busyTool !== null}>
              {busyTool === "quiz" ? "Generating..." : "Generate Quiz"}
            </button>
            <div className="mt-3 space-y-2">
              {quizItems.length === 0 ? (
                <div className="sb-empty">Create MCQs and short-answer checks from your uploaded knowledge.</div>
              ) : (
                quizItems.map((item, index) => (
                  <article key={`${item.question}-${index}`} className="sb-list-item block">
                    <p className="text-sm font-medium text-[var(--text-primary)]">{index + 1}. {item.question}</p>
                    {item.options?.length ? (
                      <ul className="mt-2 space-y-1 text-xs text-[var(--text-secondary)]">
                        {item.options.map((option, optionIndex) => (
                          <li key={`${option}-${optionIndex}`}>• {option}</li>
                        ))}
                      </ul>
                    ) : null}
                    <p className="mt-2 text-xs text-[var(--text-primary)]">Answer: {item.answer}</p>
                  </article>
                ))
              )}
            </div>
          </>
        ) : null}

        {activeTab === "flashcards" ? (
          <>
            <button
              type="button"
              className="sb-secondary-btn w-full"
              onClick={onGenerateFlashcards}
              disabled={busyTool !== null}
            >
              {busyTool === "flashcards" ? "Generating..." : "Generate Flashcards"}
            </button>
            <div className="mt-3 grid gap-2">
              {flashcards.length === 0 ? (
                <div className="sb-empty">Generate question-answer flashcards for revision and viva prep.</div>
              ) : (
                flashcards.map((card, index) => (
                  <article key={`${card.front}-${index}`} className="sb-list-item block">
                    <p className="text-xs uppercase tracking-wide text-[var(--text-secondary)]">Front</p>
                    <p className="text-sm text-[var(--text-primary)]">{card.front}</p>
                    <p className="mt-2 text-xs uppercase tracking-wide text-[var(--text-secondary)]">Back</p>
                    <p className="text-sm text-[var(--text-primary)]">{card.back}</p>
                  </article>
                ))
              )}
            </div>
          </>
        ) : null}

        {activeTab === "mindmap" ? (
          <>
            <button
              type="button"
              className="sb-secondary-btn w-full"
              onClick={onGenerateMindMap}
              disabled={busyTool !== null}
            >
              {busyTool === "mindmap" ? "Generating..." : "Generate Mind Map"}
            </button>
            <div className="mt-3 h-[440px] overflow-hidden rounded-2xl border border-[var(--border-soft)]">
              {rfNodes.length === 0 ? (
                <div className="sb-empty h-full">Build a concept graph from your sources to visualize connections.</div>
              ) : (
                <ReactFlow nodes={rfNodes} edges={rfEdges} fitView proOptions={{ hideAttribution: true }}>
                  <MiniMap pannable zoomable />
                  <Controls />
                  <Background />
                </ReactFlow>
              )}
            </div>
          </>
        ) : null}
      </div>
    </aside>
  );
}
