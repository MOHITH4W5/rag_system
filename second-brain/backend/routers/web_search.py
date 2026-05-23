from fastapi import APIRouter, HTTPException

from core.llm import web_search
from schemas.models import WebSearchRequest

router = APIRouter(tags=["web"])


@router.post("/web-search")
def search(payload: WebSearchRequest):
    try:
        return web_search(payload.query, max_results=payload.max_results)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
