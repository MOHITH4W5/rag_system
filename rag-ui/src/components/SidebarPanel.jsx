function HealthBadge({ connected }) {
  return (
    <div className={`health-badge ${connected ? "online" : "offline"}`}>
      <span className="health-dot" aria-hidden="true" />
      <span>{connected ? "Model runtime connected" : "Model runtime unavailable"}</span>
    </div>
  );
}

function UploadArea({ dragging, uploading, onOpenPicker, onDrop, onDragOver, onDragLeave, statusMsg }) {
  return (
    <section className="panel section-card upload-card">
      <div className="section-head">
        <h3>Ingestion</h3>
        <p>PDF, TXT, DOCX</p>
      </div>

      <button
        type="button"
        className={`upload-zone ${dragging ? "drag" : ""}`}
        onClick={onOpenPicker}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
      >
        <span className="upload-title">Drop file to index</span>
        <span className="upload-subtitle">or choose from your system</span>
      </button>

      {uploading && (
        <div className="progress-wrap" aria-live="polite">
          <div className="progress-bar" />
          <span className="progress-label">Chunking and embedding in progress...</span>
        </div>
      )}

      {statusMsg && (
        <p className={`status-message ${statusMsg.type || "info"}`} role="status">
          {statusMsg.text}
        </p>
      )}
    </section>
  );
}

function DocumentsList({ docs, onDelete }) {
  return (
    <section className="panel section-card documents-card">
      <div className="section-head">
        <h3>Document Library</h3>
        <span className="pill-count">{docs.length}</span>
      </div>

      {docs.length === 0 ? (
        <p className="empty-copy">No documents available yet. Upload one to start retrieval.</p>
      ) : (
        <ul className="doc-list" aria-label="Uploaded documents">
          {docs.map((doc) => (
            <li key={doc.id} className="doc-item">
              <div className="doc-meta">
                <span className="doc-file" title={doc.filename}>
                  {doc.filename}
                </span>
                <span className="doc-chunks">{doc.chunk_count} chunks indexed</span>
              </div>
              <button
                type="button"
                className="icon-btn skeuo-control"
                onClick={() => onDelete(doc.id)}
                aria-label={`Delete ${doc.filename}`}
                title="Delete document"
              >
                Del
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default function SidebarPanel({
  llmConnected,
  dragging,
  uploading,
  statusMsg,
  docs,
  fileInputRef,
  onDrop,
  onDragOver,
  onDragLeave,
  onFileChange,
  onDelete,
}) {
  return (
    <div className="sidebar-content">
      <section className="brand-row panel">
        <div className="brand-mark" aria-hidden="true">
          RS
        </div>
        <div className="brand-copy">
          <h2>RAG Studio Pro</h2>
          <p>Portfolio SaaS Intelligence Layer</p>
        </div>
      </section>

      <HealthBadge connected={llmConnected} />

      <UploadArea
        dragging={dragging}
        uploading={uploading}
        onOpenPicker={() => fileInputRef.current?.click()}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        statusMsg={statusMsg}
      />

      <DocumentsList docs={docs} onDelete={onDelete} />

      <input ref={fileInputRef} className="hidden-input" type="file" accept=".pdf,.txt,.docx" onChange={onFileChange} />
    </div>
  );
}
