from fastapi import APIRouter, Depends, HTTPException

from core.llm import build_mindmap
from core.security import get_current_user
from schemas.models import MindMapRequest

router = APIRouter(tags=["graph"])


@router.post("/mindmap")
def mindmap(payload: MindMapRequest, current_user: dict = Depends(get_current_user)):
    try:
        return build_mindmap(topic=payload.topic, max_nodes=payload.max_nodes, current_user=current_user)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
