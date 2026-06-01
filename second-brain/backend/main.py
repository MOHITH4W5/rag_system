import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from app.database import init_db  # noqa: E402
from core.bootstrap import (  # noqa: E402
    backfill_existing_documents_to_admin_global,
    ensure_multitenant_schema,
    seed_demo_users,
)
from routers.auth import router as auth_router  # noqa: E402
from routers.documents import router as documents_router  # noqa: E402
from routers.engine import router as engine_router  # noqa: E402
from routers.ingest import router as ingest_router  # noqa: E402
from routers.mindmap import router as mindmap_router  # noqa: E402
from routers.query import router as query_router  # noqa: E402
from routers.quiz import router as quiz_router  # noqa: E402
from routers.web_search import router as web_search_router  # noqa: E402


def _parse_origins() -> list[str]:
    raw = os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001",
    )
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        init_db()
        ensure_multitenant_schema()
        seed_demo_users()
        backfill_existing_documents_to_admin_global()
        print("[Second-Brain API] Database schema initialized")
    except Exception as exc:
        print(f"[Second-Brain API] Warning: schema init failed: {exc}")
    yield


app = FastAPI(
    title="Second Brain API",
    description="NotebookLM-inspired multimodal RAG backend",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": "Second Brain API",
        "status": "running",
        "docs": "/docs",
        "ui": "http://localhost:3001",
    }


app.include_router(engine_router)
app.include_router(auth_router)
app.include_router(ingest_router)
app.include_router(query_router)
app.include_router(web_search_router)
app.include_router(quiz_router)
app.include_router(mindmap_router)
app.include_router(documents_router)
