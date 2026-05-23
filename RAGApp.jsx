import React, { useState, useEffect, useRef, useCallback } from 'react';

const STYLES = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Fraunces:ital,opsz,wght@1,9..144,400;1,9..144,600&family=JetBrains+Mono:wght@400;500&display=swap');

  :root {
    --bg-base: #0d0f14;
    --surface-1: rgba(255, 255, 255, 0.06);
    --surface-2: rgba(255, 255, 255, 0.10);
    --surface-3: rgba(255, 255, 255, 0.15);
    
    --clay-1: #c8b8ff;
    --clay-2: #b8f0e0;
    --clay-3: #ffd6b8;
    --clay-4: #b8d8ff;

    --text-primary: #f0f0f5;
    --text-muted: rgba(240, 240, 245, 0.45);
    --text-ghost: rgba(240, 240, 245, 0.18);

    --glass-border: 1px solid rgba(255, 255, 255, 0.12);
  }

  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  body {
    background-color: var(--bg-base);
    color: var(--text-primary);
    font-family: 'DM Sans', sans-serif;
    overflow: hidden;
    height: 100vh;
  }

  /* Utility / Morphism Classes */
  .glass-panel {
    background: var(--surface-1);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: var(--glass-border);
    border-top: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1), inset 0 -1px 0 rgba(255, 255, 255, 0.05);
  }

  .skeuo-paper {
    background-color: #f7f7f9;
    color: #1a1a1a;
    background-image: repeating-linear-gradient(0deg, transparent, transparent 1px, rgba(0,0,0,0.02) 1px, rgba(0,0,0,0.02) 2px);
    box-shadow: inset 0 0 10px rgba(0,0,0,0.05), inset 1px 1px 1px rgba(255,255,255,0.8), 2px 4px 15px rgba(0,0,0,0.2), 0 1px 3px rgba(0,0,0,0.1);
    border-radius: 4px;
    position: relative;
    transition: transform 0.3s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.3s ease;
  }
  
  .skeuo-paper::after {
    content: '';
    position: absolute;
    bottom: 0; right: 0;
    width: 20px; height: 20px;
    background: linear-gradient(to top left, transparent 50%, rgba(0,0,0,0.1) 50%);
    border-bottom-right-radius: 4px;
    transition: background 0.3s ease;
  }

  .skeuo-recessed {
    background: rgba(0, 0, 0, 0.2);
    box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.6), inset 0 0 2px rgba(0, 0, 0, 0.8), 0 1px 1px rgba(255, 255, 255, 0.05);
    transition: box-shadow 0.3s ease, background 0.3s ease;
  }
  .skeuo-recessed:focus-within {
    background: rgba(0, 0, 0, 0.15);
    box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.7), inset 0 0 2px rgba(0, 0, 0, 0.9), 0 1px 1px rgba(255, 255, 255, 0.1), 0 0 10px rgba(184, 240, 224, 0.1);
  }

  .clay-puffy {
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.4), 0 8px 20px rgba(0,0,0,0.2), inset 0 4px 10px rgba(255,255,255,0.5), inset 0 -4px 10px rgba(0,0,0,0.15);
    transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  
  .clay-puffy:hover {
    transform: scale(1.02) translateY(-2px);
    box-shadow: 0 25px 65px rgba(0,0,0,0.45), 0 12px 25px rgba(0,0,0,0.25), inset 0 4px 12px rgba(255,255,255,0.6), inset 0 -4px 10px rgba(0,0,0,0.15);
  }
  .clay-puffy:active {
    transform: scale(0.94);
    box-shadow: 0 10px 30px rgba(0,0,0,0.4), 0 6px 12px rgba(0,0,0,0.2), inset 0 2px 6px rgba(255,255,255,0.3), inset 0 -2px 6px rgba(0,0,0,0.1);
  }

  /* Layout */
  .layout {
    display: flex;
    height: 100vh;
    width: 100vw;
  }

  .sidebar {
    width: 280px;
    height: 100%;
    display: flex;
    flex-direction: column;
    padding: 24px;
    gap: 32px;
    border-right: var(--glass-border);
    z-index: 10;
  }

  .main {
    flex: 1;
    display: flex;
    flex-direction: column;
    position: relative;
    height: 100%;
  }

  /* Sidebar Elements */
  .logo-area {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  
  .logo-badge {
    width: 48px;
    height: 48px;
    background: var(--clay-1);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    color: #1a1a1a;
  }

  .logo-text {
    font-family: 'Fraunces', serif;
    font-style: italic;
    font-size: 20px;
    font-weight: 600;
  }

  .status-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: var(--text-muted);
    font-family: 'JetBrains Mono', monospace;
    margin-top: 4px;
  }

  .led {
    width: 8px;
    height: 8px;
    background: #4ade80;
    border-radius: 50%;
    box-shadow: inset 0 1px 2px rgba(255,255,255,0.8), 0 0 10px #4ade80, 0 0 20px rgba(74, 222, 128, 0.4);
    animation: pulse-led 2s infinite;
  }
  .led.offline {
    background: #ef4444;
    box-shadow: inset 0 1px 2px rgba(255,255,255,0.8), 0 0 10px #ef4444, 0 0 20px rgba(239, 68, 68, 0.4);
  }

  @keyframes pulse-led {
    0% { opacity: 0.8; box-shadow: 0 0 10px currentColor; }
    50% { opacity: 1; box-shadow: 0 0 15px currentColor, 0 0 30px currentColor; }
    100% { opacity: 0.8; box-shadow: 0 0 10px currentColor; }
  }

  .upload-zone {
    border: 2px dashed rgba(255,255,255,0.2);
    border-radius: 12px;
    padding: 24px 16px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    position: relative;
    overflow: hidden;
  }
  .upload-zone:hover, .upload-zone.drag-over {
    background: var(--surface-2);
    border-color: var(--clay-2);
    transform: scale(1.02);
    box-shadow: 0 12px 30px rgba(0,0,0,0.3), inset 0 0 20px rgba(184, 240, 224, 0.05);
  }
  .upload-zone:active {
    transform: scale(0.98);
  }
  
  .upload-icon {
    font-size: 24px;
    margin-bottom: 8px;
    color: var(--clay-2);
  }
  
  .upload-text {
    font-size: 13px;
    color: var(--text-muted);
  }

  .upload-progress-bar {
    height: 6px;
    background: var(--clay-2);
    border-radius: 3px;
    margin-top: 12px;
    box-shadow: inset 0 1px 2px rgba(255,255,255,0.5);
    transition: width 0.3s ease;
  }

  .doc-list {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding-right: 8px;
  }
  
  .doc-list::-webkit-scrollbar {
    width: 4px;
  }
  .doc-list::-webkit-scrollbar-thumb {
    background: var(--surface-3);
    border-radius: 2px;
  }

  .doc-card {
    padding: 12px;
    border-radius: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
    transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s ease;
  }
  .doc-card:hover {
    transform: translateY(-4px) scale(1.01) rotate(0.5deg);
    box-shadow: 0 15px 30px rgba(0,0,0,0.4), 0 5px 10px rgba(0,0,0,0.2);
  }
  .doc-card:hover::after {
    background: linear-gradient(to top left, transparent 50%, rgba(0,0,0,0.15) 50%);
  }
  .doc-name {
    font-size: 13px;
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 160px;
  }

  .doc-delete {
    opacity: 0;
    background: none;
    border: none;
    color: var(--clay-3);
    cursor: pointer;
    font-size: 16px;
    transition: opacity 0.2s;
  }
  .doc-card:hover .doc-delete {
    opacity: 1;
  }

  /* Main Area */
  .header {
    height: 80px;
    padding: 0 40px;
    display: flex;
    align-items: center;
    border-bottom: var(--glass-border);
    z-index: 10;
  }
  .header-title {
    font-family: 'Fraunces', serif;
    font-style: italic;
    font-size: 32px;
    font-weight: 400;
  }

  .chat-area {
    flex: 1;
    overflow-y: auto;
    padding: 40px;
    display: flex;
    flex-direction: column;
    gap: 24px;
    scroll-behavior: smooth;
  }

  .welcome-state {
    margin: auto;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 32px;
    animation: fade-in-up 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
  }
  
  .orbiting-docs {
    position: relative;
    width: 120px;
    height: 120px;
  }
  .central-sparkle {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    font-size: 48px;
    text-shadow: 0 0 20px var(--clay-1);
  }
  .orbit-item {
    position: absolute;
    top: 50%; left: 50%;
    width: 40px; height: 50px;
    margin: -25px 0 0 -20px;
    animation: orbit 10s linear infinite;
  }
  @keyframes orbit {
    0% { transform: rotate(0deg) translateX(80px) rotate(0deg); }
    100% { transform: rotate(360deg) translateX(80px) rotate(-360deg); }
  }

  .suggestion-chips {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    justify-content: center;
  }
  .chip {
    padding: 12px 24px;
    border: none;
    border-radius: 30px;
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
    font-weight: 500;
    color: #1a1a1a;
    cursor: pointer;
    transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), filter 0.3s ease;
  }
  .chip:hover {
    filter: brightness(1.05);
    transform: scale(1.05) translateY(-2px) rotate(-1deg);
  }

  /* Messages */
  .message-wrapper {
    display: flex;
    width: 100%;
    animation: fade-in-up 0.35s ease forwards;
  }
  .message-wrapper.user {
    justify-content: flex-end;
  }

  .msg-user {
    background: var(--clay-1);
    color: #1a1a1a;
    padding: 16px 24px;
    max-width: 60%;
    transform: rotate(-0.5deg);
    border-bottom-right-radius: 4px;
  }

  .msg-assistant {
    padding: 24px;
    max-width: 70%;
    border-bottom-left-radius: 4px;
    position: relative;
  }

  .msg-content {
    line-height: 1.6;
    font-size: 15px;
    white-space: pre-wrap;
  }

  .sources-container {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px dashed rgba(0,0,0,0.1);
  }
  .source-tag {
    background: #ffebb3;
    color: #4d3e00;
    padding: 4px 10px;
    font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
    border-radius: 2px;
    box-shadow: 1px 2px 4px rgba(0,0,0,0.1);
    transform: rotate(-1deg);
  }
  .response-time {
    position: absolute;
    bottom: -20px;
    left: 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: var(--text-ghost);
  }

  /* Input Area */
  .input-area-wrapper {
    padding: 24px 40px 40px;
    background: linear-gradient(to top, var(--bg-base) 60%, transparent);
    z-index: 10;
  }

  .input-container {
    display: flex;
    align-items: flex-end;
    gap: 16px;
    padding: 12px;
    border-radius: 24px;
  }

  .paperclip {
    color: var(--text-muted);
    font-size: 20px;
    padding: 12px;
    cursor: pointer;
    transition: color 0.2s;
  }
  .paperclip:hover {
    color: var(--text-primary);
  }

  .textarea-wrapper {
    flex: 1;
    border-radius: 16px;
    padding: 2px;
  }

  textarea {
    width: 100%;
    background: transparent;
    border: none;
    color: var(--text-primary);
    font-family: 'DM Sans', sans-serif;
    font-size: 15px;
    line-height: 1.5;
    padding: 14px 16px;
    resize: none;
    outline: none;
  }
  textarea::placeholder {
    color: var(--text-muted);
  }

  .send-btn {
    width: 48px;
    height: 48px;
    border: none;
    background: var(--clay-4);
    color: #1a1a1a;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    cursor: pointer;
    flex-shrink: 0;
    transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.3s ease, filter 0.3s ease;
  }
  .send-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: scale(1) !important;
    filter: grayscale(0.5);
  }
  .send-btn:not(:disabled):hover {
    transform: scale(1.05) rotate(5deg);
  }

  /* Animations */
  @keyframes fade-in-up {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .typing-indicator {
    display: flex;
    gap: 6px;
    padding: 16px 24px;
  }
  .typing-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    animation: typing-bounce 1.4s infinite cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  .typing-dot:nth-child(1) { background: var(--clay-1); animation-delay: 0s; }
  .typing-dot:nth-child(2) { background: var(--clay-2); animation-delay: 0.15s; }
  .typing-dot:nth-child(3) { background: var(--clay-3); animation-delay: 0.3s; }

  @keyframes typing-bounce {
    0%, 80%, 100% { transform: translateY(0); }
    40% { transform: translateY(-10px); }
  }
`;

const API_BASE = 'http://localhost:8000';

export default function RAGApp() {
  const [llmStatus, setLlmStatus] = useState({ connected: false, loading: true });
  const [documents, setDocuments] = useState([]);
  const [messages, setMessages] = useState([]);
  const [inputVal, setInputVal] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isTyping, setIsTyping] = useState(false);
  const [dragOver, setDragOver] = useState(false);

  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  const fetchHealth = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/health`);
      if (res.ok) {
        setLlmStatus({ connected: true, loading: false });
      } else {
        setLlmStatus({ connected: false, loading: false });
      }
    } catch {
      setLlmStatus({ connected: false, loading: false });
    }
  }, []);

  const fetchDocuments = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/documents`);
      if (res.ok) {
        const data = await res.json();
        // Assuming API returns { documents: [...] } or just [...]
        setDocuments(Array.isArray(data) ? data : data.documents || []);
      }
    } catch (e) {
      console.error('Failed to fetch documents', e);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
    fetchDocuments();
    const interval = setInterval(fetchHealth, 10000); // Check health every 10s
    return () => clearInterval(interval);
  }, [fetchHealth, fetchDocuments]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleInput = (e) => {
    setInputVal(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const scrollHeight = textareaRef.current.scrollHeight;
      textareaRef.current.style.height = Math.min(Math.max(scrollHeight, 24), 120) + 'px';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const sendMessage = async (textOveride) => {
    const text = textOveride || inputVal.trim();
    if (!text || isTyping) return;

    setInputVal('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';

    const newMessages = [...messages, { role: 'user', content: text }];
    setMessages(newMessages);
    setIsTyping(true);

    try {
      const res = await fetch(`${API_BASE}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: text })
      });

      if (res.ok) {
        const data = await res.json();
        setMessages([...newMessages, {
          role: 'assistant',
          content: data.answer,
          sources: data.sources,
          timeMs: data.response_time_ms
        }]);
      } else {
        throw new Error('API Error');
      }
    } catch (e) {
      setMessages([...newMessages, {
        role: 'assistant',
        content: 'Sorry, I encountered an error communicating with the backend.'
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleFileUpload = async (file) => {
    if (!file) return;
    setIsUploading(true);
    setUploadProgress(10);

    // Simulate initial progress purely for visual feedback since fetch doesn't support native upload progress easily
    const progInt = setInterval(() => {
      setUploadProgress(p => p < 90 ? p + 10 : p);
    }, 150);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData,
      });
      if (res.ok) {
        clearInterval(progInt);
        setUploadProgress(100);
        await new Promise(r => setTimeout(r, 400));
        fetchDocuments();
      }
    } catch (e) {
      console.error(e);
    } finally {
      clearInterval(progInt);
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const deleteDocument = async (id, e) => {
    e.stopPropagation();
    try {
      const res = await fetch(`${API_BASE}/documents/${id}`, { method: 'DELETE' });
      if (res.ok) fetchDocuments();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <>
      <style>{STYLES}</style>
      <div className="layout">

        {/* SIDEBAR - Glass + Skeuomorphism + Clay */}
        <div className="sidebar glass-panel">
          <div className="logo-area">
            <div className="logo-badge clay-puffy">✦</div>
            <div>
              <div className="logo-text">RAG Docs</div>
              <div className="status-indicator">
                <div className={`led ${llmStatus.connected ? '' : 'offline'}`} />
                {llmStatus.connected ? 'LLM ACTIVE' : 'LLM OFFLINE'}
              </div>
            </div>
          </div>

          <div className="skeuo-recessed" style={{ height: '1px', width: '100%' }} />

          {/* Upload Zone - Skeuo tray feel */}
          <div
            className={`upload-zone skeuo-paper ${dragOver ? 'drag-over' : ''}`}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={onDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              type="file"
              ref={fileInputRef}
              style={{ display: 'none' }}
              accept=".pdf,.txt,.docx"
              onChange={(e) => handleFileUpload(e.target.files[0])}
            />
            <div className="upload-icon">📥</div>
            <div className="upload-text">Drop documents here<br />or click to browse</div>
            {isUploading && (
              <div className="upload-progress-bar" style={{ width: `${uploadProgress}%` }} />
            )}
          </div>

          <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>
            YOUR DOCUMENTS
          </div>

          <div className="doc-list">
            {documents.map((doc, i) => (
              <div key={doc.id || i} className="doc-card skeuo-paper" style={{ animationDelay: `${i * 80}ms` }}>
                <div className="doc-name">📄 {doc.filename || doc.name || `Document ${i + 1}`}</div>
                <button className="doc-delete" onClick={(e) => deleteDocument(doc.id, e)}>⌫</button>
              </div>
            ))}
            {documents.length === 0 && (
              <div style={{ color: 'var(--text-ghost)', fontSize: '13px', fontStyle: 'italic' }}>
                No documents uploaded yet.
              </div>
            )}
          </div>
        </div>

        {/* MAIN CHAT AREA */}
        <div className="main">
          {/* Header - Glass */}
          <div className="header glass-panel">
            <div>
              <h1 className="header-title">Ask Your Documents</h1>
              <div style={{ color: 'var(--text-muted)', fontSize: '14px', marginTop: '4px' }}>
                AI-powered retrieval and synthesis
              </div>
            </div>
          </div>

          {/* Chat Messages */}
          <div className="chat-area">
            {messages.length === 0 ? (
              <div className="welcome-state">
                <div className="orbiting-docs">
                  <div className="central-sparkle">✨</div>
                  <div className="orbit-item" style={{ animationDelay: '0s' }}>📄</div>
                  <div className="orbit-item" style={{ animationDelay: '-3.3s' }}>📑</div>
                  <div className="orbit-item" style={{ animationDelay: '-6.6s' }}>🗂️</div>
                </div>
                <h2 style={{ fontFamily: 'Fraunces', fontStyle: 'italic', fontSize: '36px', fontWeight: 400 }}>
                  What would you like to know?
                </h2>
                <div className="suggestion-chips">
                  <button className="chip clay-puffy" style={{ background: 'var(--clay-1)' }} onClick={() => sendMessage("Summarize the main topics.")}>Summarize topics</button>
                  <button className="chip clay-puffy" style={{ background: 'var(--clay-2)' }} onClick={() => sendMessage("What are the key insights?")}>Key insights</button>
                  <button className="chip clay-puffy" style={{ background: 'var(--clay-3)' }} onClick={() => sendMessage("Find any action items.")}>Action items</button>
                  <button className="chip clay-puffy" style={{ background: 'var(--clay-4)' }} onClick={() => sendMessage("Explain the core concept.")}>Core concept</button>
                </div>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div key={idx} className={`message-wrapper ${msg.role}`}>
                  {msg.role === 'user' ? (
                    <div className="msg-user clay-puffy">
                      <div className="msg-content">{msg.content}</div>
                    </div>
                  ) : (
                    <div className="msg-assistant skeuo-paper glass-panel" style={{ background: 'rgba(255,255,255,0.85)' }}>
                      <div className="msg-content">{msg.content}</div>

                      {msg.sources && msg.sources.length > 0 && (
                        <div className="sources-container">
                          {msg.sources.map((src, sIdx) => (
                            <div key={sIdx} className="source-tag">
                              📌 {src.filename} ({(src.relevance_score || 0).toFixed(2)})
                            </div>
                          ))}
                        </div>
                      )}

                      {msg.timeMs && (
                        <div className="response-time">⏱ {msg.timeMs}ms</div>
                      )}
                    </div>
                  )}
                </div>
              ))
            )}

            {isTyping && (
              <div className="message-wrapper assistant">
                <div className="msg-assistant glass-panel typing-indicator">
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="input-area-wrapper">
            <div className="input-container glass-panel">
              <div className="paperclip" onClick={() => fileInputRef.current?.click()}>📎</div>
              <div className="textarea-wrapper skeuo-recessed">
                <textarea
                  ref={textareaRef}
                  value={inputVal}
                  onChange={handleInput}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask a question about your documents..."
                  rows={1}
                />
              </div>
              <button
                className="send-btn clay-puffy"
                onClick={() => sendMessage()}
                disabled={!inputVal.trim() || isTyping}
              >
                ↑
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
