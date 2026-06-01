from fastapi import APIRouter, Depends, HTTPException

from core.llm import web_search
from core.security import get_current_user
from schemas.models import WebSearchRequest

router = APIRouter(tags=["web"])


@router.post("/web-search")
def search(payload: WebSearchRequest, _: dict = Depends(get_current_user)):
    try:
        return web_search(payload.query, max_results=payload.max_results)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
