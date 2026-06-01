# Second Brain (NotebookLM-Inspired)

This is a **NotebookLM-style** app with additional features:
- Multimodal source ingestion pipeline (text now, extensible for audio/video/image)
- Hybrid retrieval (`local docs + optional live web`)
- Runtime engine switch (`langchain` / `classic`)
- Study tools (`quiz`, `flashcards`, `mindmap`)

## URL Map
- UI: `http://localhost:3001`
- API Docs: `http://localhost:8001/docs`
- API Health: `http://localhost:8001/health`
- Engine State: `http://localhost:8001/engine`

## Demo Login Accounts
- `admin / admin123`
- `user1 / user123`
- `user2 / user123`

You can override defaults with env vars:
- `SEED_ADMIN_PASSWORD`
- `SEED_USER1_PASSWORD`
- `SEED_USER2_PASSWORD`

## Run Locally (without Docker)
From `C:\rag_system`:

1. Start Ollama and keep it running:
```powershell
ollama serve
```

2. Start backend:
```powershell
cd C:\rag_system\second-brain\backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

3. Start frontend:
```powershell
cd C:\rag_system\second-brain\frontend
npm install
npm run dev
```

## One-Command Docker Startup
From `C:\rag_system`:

```powershell
docker compose -f docker-compose.second-brain.yml up --build
```

This starts:
- `sb_ollama` (Ollama runtime, port `11434`)
- `sb_postgres` (PostgreSQL)
- `sb_backend` (FastAPI, port `8001`)
- `sb_frontend` (Next.js, port `3001`)

After first startup, pull model once:

```powershell
docker compose -f docker-compose.second-brain.yml exec sb_ollama ollama pull llama3
```

Then ask questions from UI normally.

## Core Endpoints
- `POST /auth/login` - login and receive bearer token
- `GET /auth/me` - current logged-in user
- `POST /ingest` - upload and index a source
- `POST /query` - RAG answer (`use_web=true` for hybrid path)
- `POST /web-search` - live web context (Tavily if `TAVILY_API_KEY` is set)
- `POST /quiz` - generate quiz from source context
- `POST /flashcards` - generate flashcards
- `POST /mindmap` - generate graph JSON for concept mapping
- `GET /engine`, `POST /engine` - runtime engine control

All data endpoints are authenticated. `POST /engine` is admin-only.

## DBMS Viva Flow (2-3 min)
1. Open UI `http://localhost:3001`
2. Upload one document, ask one question
3. Show health JSON at `http://localhost:8001/health`
4. Show DB proof:
```powershell
docker exec -it sb_postgres psql -U postgres -d rag_db
```
```sql
\dt
SELECT id, filename, file_type, upload_date FROM documents ORDER BY id DESC LIMIT 5;
SELECT d.id, d.filename, COUNT(dc.id) AS chunk_count
FROM documents d
LEFT JOIN document_chunks dc ON dc.document_id = d.id
GROUP BY d.id, d.filename
ORDER BY d.id DESC;
SELECT id, question, response_time_ms, created_at FROM query_logs ORDER BY id DESC LIMIT 5;
```

## Notes
- First build is heavy because Python ML dependencies download large packages.
- If web search should be truly live, set `TAVILY_API_KEY` in backend environment.
