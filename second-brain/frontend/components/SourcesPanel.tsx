"use client";

import { FileText, Trash2, UploadCloud } from "lucide-react";

import type { DocumentItem } from "@/lib/types";

type Props = {
  documents: DocumentItem[];
  uploadBusy: boolean;
  onUploadClick: () => void;
  onDelete: (docId: number) => void;
};

export function SourcesPanel({ documents, uploadBusy, onUploadClick, onDelete }: Props) {
  return (
    <aside className="sb-panel min-h-[400px]">
      <div className="flex items-center justify-between">
        <h2 className="sb-section-title">Sources</h2>
        <span className="sb-badge">{documents.length} items</span>
      </div>

      <button type="button" onClick={onUploadClick} className="sb-primary-btn mt-4 w-full" disabled={uploadBusy}>
        <UploadCloud size={16} />
        {uploadBusy ? "Uploading..." : "Add Source"}
      </button>

      <div className="mt-4 space-y-2">
        {documents.length === 0 ? (
          <div className="sb-empty">
            <p className="font-medium text-[var(--text-primary)]">No sources yet</p>
            <p className="mt-1 text-xs text-[var(--text-secondary)]">
              Upload PDF, DOCX, TXT, audio, or video to build your grounded knowledge base.
            </p>
          </div>
        ) : (
          documents.map((doc) => (
            <article key={doc.id} className="sb-list-item">
              <div className="flex min-w-0 items-start gap-2">
                <FileText size={14} className="mt-0.5 shrink-0 text-[var(--accent)]" />
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-[var(--text-primary)]">{doc.filename}</p>
                  <p className="text-xs text-[var(--text-secondary)]">{doc.chunk_count} chunks</p>
                </div>
              </div>
              <button
                type="button"
                className="sb-icon-btn danger"
                aria-label={`Delete ${doc.filename}`}
                onClick={() => onDelete(doc.id)}
              >
                <Trash2 size={14} />
              </button>
            </article>
          ))
        )}
      </div>
    </aside>
  );
}
