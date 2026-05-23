# RAG Document Management System

An end-to-end local RAG (Retrieval-Augmented Generation) project for DBMS portfolio work.

## What this project includes

- PostgreSQL for document/chunk/query metadata
- FAISS for vector similarity search
- Sentence Transformers (`all-MiniLM-L6-v2`) for embeddings
- Ollama (`llama3`) for local LLM answers
- LangChain integration (`langchain` + `langchain-ollama`) with engine switching
- FastAPI backend for upload/query/document management
- React frontend (`rag-ui`) and optional Streamlit UI

## Architecture

`Upload -> Parse -> Chunk -> PostgreSQL -> Embed -> FAISS -> Retrieve -> LLM -> Answer + Sources`

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Ollama installed locally

## Demo URL Map (Important)

- UI app (open this in browser): [http://localhost:3000](http://localhost:3000)
- API root: [http://localhost:8000](http://localhost:8000)
- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health JSON (expected JSON response): [http://localhost:8000/health](http://localhost:8000/health)

Notes:
- `localhost:3000` is the React UI.
- `localhost:8000/health` is backend JSON by design (`llm_connected`, `rag_engine`).

## UI Walkthrough (Portfolio Demo)

Use these checkpoints while showcasing the product:

1. Dashboard overview
- Open [http://localhost:3000](http://localhost:3000)
- Point out: indexed document count, runtime status, active engine, theme toggle

2. Ingestion workflow
- Use the left `Ingestion` card to upload a file
- Highlight progress feedback and resulting document count update

3. Retrieval + generation
- Ask a question in the conversation panel
- Show response source chips, latency, and engine badge (`langchain` or `classic`)

4. Engine switching (no restart)
- Toggle engine in header (`LangChain` / `Classic`)
- Ask a follow-up question to demonstrate runtime switch behavior

5. Backend + DB proof
- Show [http://localhost:8000/health](http://localhost:8000/health)
- Run SQL checks from the `Viva Flow` section to prove persisted DB state

## One-command Docker startup

1. Start Ollama on your host machine:

```bash
ollama pull llama3
ollama serve
```

2. From project root run:

```bash
docker compose up --build
```

3. Open:

- UI: [http://localhost:3000](http://localhost:3000)
- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

Notes:
- Compose starts `Postgres + FastAPI + UI` together.
- Postgres uses default container credentials: `postgres/postgres` with DB `rag_db`.
- Database data persists in Docker volume `postgres_data`.
- FAISS index persists via `./data` bind mount.

## Viva Flow (DBMS Demo)

1. Open UI and show product flow

- [http://localhost:3000](http://localhost:3000)
- Upload a file and ask one question

2. Show backend health and engine mode

- Open [http://localhost:8000/health](http://localhost:8000/health)
- Explain `llm_connected` and `rag_engine`

3. Show database evidence live

```bash
docker exec -it rag_db psql -U postgres -d rag_db
```

Then run:

```sql
\dt
SELECT id, filename, file_type, upload_date FROM documents ORDER BY id DESC LIMIT 5;
SELECT d.id, d.filename, COUNT(dc.id) AS chunk_count
FROM documents d
LEFT JOIN document_chunks dc ON dc.document_id = d.id
GROUP BY d.id, d.filename
ORDER BY d.id DESC;
SELECT id, question, retrieved_chunk_ids, response_time_ms, created_at
FROM query_logs
ORDER BY id DESC
LIMIT 5;
```

## 1) Setup backend

```bash
cd C:\rag_system
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

RAG engine mode (optional):

```bash
# LangChain path (default)
set RAG_ENGINE=langchain

# Classic custom path
set RAG_ENGINE=classic
```

Create a `.env` file:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rag_db
DB_USER=postgres
DB_PASSWORD=your_password

# Optional: allowed CORS origins for React
FRONTEND_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

Create database and run schema:

```sql
CREATE DATABASE rag_db;
```

Then apply schema:

```bash
psql -U postgres -d rag_db -f schema.sql
```

Note: the API also calls `init_db()` on startup, and the schema is idempotent (`IF NOT EXISTS`).

## 2) Setup Ollama

```bash
ollama pull llama3
ollama serve
```

## 3) Run FastAPI backend

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## 4) Run React frontend

```bash
cd rag-ui
npm install
npm start
```

Open [http://localhost:3000](http://localhost:3000)

Optional frontend env (`rag-ui/.env`):

```env
REACT_APP_API_BASE=http://localhost:8000
```

## 5) Optional Streamlit UI

```bash
streamlit run app/ui.py
```

## Useful API endpoints

- `GET /health` -> LLM connectivity + active RAG engine
- `POST /upload` -> upload and index document
- `POST /ask` -> ask question
- `GET /documents` -> list documents
- `DELETE /documents/{doc_id}` -> delete one document
- `DELETE /clear-all` -> reset all data
- `GET /stats` -> system counters

## Common troubleshooting

- Backend fails to connect DB: verify `.env` credentials and PostgreSQL service
- Upload fails: ensure `python-multipart` is installed
- No answers: ensure `ollama serve` is running and `llama3` exists
- Empty results: upload documents first and verify `/documents` shows rows
- To compare implementations for demos: switch `RAG_ENGINE` between `langchain` and `classic`
