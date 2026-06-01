from fastapi import APIRouter, Depends, HTTPException

from core.engine_state import get_engine
from core.llm import web_search
from core.retriever import run_query
from core.security import get_current_user
from schemas.models import QueryRequest

router = APIRouter(tags=["query"])


@router.post("/query")
def query(payload: QueryRequest, current_user: dict = Depends(get_current_user)):
    try:
        answer = run_query(
            question=payload.question,
            top_k=payload.top_k,
            engine=get_engine(),
            current_user=current_user,
        )

        web = None
        if payload.use_web:
            web = web_search(payload.question, max_results=5)

        return {
            **answer,
            "runtime_engine": get_engine(),
            "web_context": web,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
