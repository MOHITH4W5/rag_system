from fastapi import APIRouter, Depends, HTTPException

from core.llm import build_flashcards, build_quiz
from core.security import get_current_user
from schemas.models import FlashcardRequest, QuizRequest

router = APIRouter(tags=["study"])


@router.post("/quiz")
def quiz(payload: QuizRequest, current_user: dict = Depends(get_current_user)):
    try:
        return build_quiz(topic=payload.topic, num_questions=payload.num_questions, current_user=current_user)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/flashcards")
def flashcards(payload: FlashcardRequest, current_user: dict = Depends(get_current_user)):
    try:
        return build_flashcards(topic=payload.topic, count=payload.count, current_user=current_user)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
