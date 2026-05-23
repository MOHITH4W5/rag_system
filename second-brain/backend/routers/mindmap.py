from fastapi import APIRouter, HTTPException

from core.llm import build_mindmap
from schemas.models import MindMapRequest

router = APIRouter(tags=["graph"])


@router.post("/mindmap")
def mindmap(payload: MindMapRequest):
    try:
        return build_mindmap(topic=payload.topic, max_nodes=payload.max_nodes)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
