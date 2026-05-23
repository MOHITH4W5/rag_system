from fastapi import APIRouter, HTTPException

from app.llm import check_ollama_health

from core.engine_state import get_engine, set_engine
from schemas.models import EngineRequest

router = APIRouter(tags=["engine"])


@router.get("/engine")
def get_runtime_engine():
    return {"engine": get_engine()}


@router.post("/engine")
def update_runtime_engine(payload: EngineRequest):
    try:
        active = set_engine(payload.engine)
        return {"success": True, "engine": active}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/health")
def health():
    return {"llm_connected": check_ollama_health(), "rag_engine": get_engine()}
