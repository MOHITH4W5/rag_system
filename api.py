import os
import tempfile
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.config import RAG_ENGINE, VALID_RAG_ENGINES
from app.database import get_db_connection, init_db


def _parse_origins() -> list[str]:
    raw = os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173",
    )
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        init_db()
        print("[API] Database schema initialized")
    except Exception as exc:
        print(f"[API] Warning: could not initialize schema: {exc}")
    yield


app = FastAPI(title="RAG Document API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

_runtime_engine = RAG_ENGINE if RAG_ENGINE in VALID_RAG_ENGINES else "langchain"


def get_runtime_engine() -> str:
    return _runtime_engine


def set_runtime_engine(engine: str):
    global _runtime_engine
    _runtime_engine = engine


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class EngineUpdateRequest(BaseModel):
    engine: Literal["langchain", "classic"]


@app.get("/")
def root():
    return {"status": "RAG API is running"}


@app.get("/health")
def health():
    try:
        from app.llm import check_ollama_health

        ok = check_ollama_health()
        return {"llm_connected": ok, "rag_engine": get_runtime_engine()}
    except Exception as exc:
        return {"llm_connected": False, "rag_engine": get_runtime_engine(), "error": str(exc)}


@app.get("/engine")
def get_engine():
    return {"engine": get_runtime_engine()}


@app.post("/engine")
def set_engine(request: EngineUpdateRequest):
    target = request.engine.strip().lower()
    if target not in VALID_RAG_ENGINES:
        raise HTTPException(status_code=400, detail=f"Invalid engine '{request.engine}'")
    set_runtime_engine(target)
    return {"success": True, "engine": get_runtime_engine()}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    tmp_path = None
    try:
        suffix = os.path.splitext(file.filename or "")[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        from app.embeddings_manager import embed_document
        from app.ingestion import ingest_document

        doc_id = ingest_document(tmp_path, file.filename or "uploaded_file")
        n_chunks = embed_document(doc_id)

        return {
            "success": True,
            "document_id": doc_id,
            "chunks_processed": n_chunks,
            "filename": file.filename,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.post("/ask")
def ask_question(request: QuestionRequest):
    try:
        from app.pipeline import ask

        return ask(request.question, top_k=request.top_k, engine=get_runtime_engine())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/documents")
def list_documents():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT d.id, d.filename, d.upload_date,
                           COUNT(dc.id) AS chunk_count
                    FROM documents d
                    LEFT JOIN document_chunks dc ON dc.document_id = d.id
                    GROUP BY d.id, d.filename, d.upload_date
                    ORDER BY d.upload_date DESC
                    """
                )
                rows = cursor.fetchall()

        return [
            {
                "id": r[0],
                "filename": r[1],
                "uploaded_at": str(r[2]),
                "chunk_count": r[3],
            }
            for r in rows
        ]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.delete("/documents/{doc_id}")
def delete_document(doc_id: int):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM document_chunks WHERE document_id = %s", (doc_id,))
                chunk_ids = [r[0] for r in cursor.fetchall()]

                if chunk_ids:
                    from app.vector_store import FAISSVectorStore

                    store = FAISSVectorStore()
                    store.delete_by_chunk_ids(chunk_ids)

                cursor.execute("DELETE FROM documents WHERE id = %s", (doc_id,))
            conn.commit()
        return {"success": True}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.delete("/clear-all")
def clear_all():
    """Delete all documents/chunks/embeddings and reset FAISS index."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM document_chunks")
                chunk_ids = [r[0] for r in cursor.fetchall()]

                if chunk_ids:
                    from app.vector_store import FAISSVectorStore

                    store = FAISSVectorStore()
                    store.delete_by_chunk_ids(chunk_ids)

                cursor.execute("DELETE FROM query_logs")
                cursor.execute("DELETE FROM documents")
            conn.commit()

        return {"success": True, "message": "All data cleared"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/stats")
def stats():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM documents")
                documents = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM document_chunks")
                chunks = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM embeddings_metadata")
                embedded = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM query_logs")
                queries = cursor.fetchone()[0]

        return {
            "documents": documents,
            "chunks": chunks,
            "embedded_chunks": embedded,
            "queries_logged": queries,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
