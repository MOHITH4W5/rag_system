from fastapi import APIRouter, HTTPException

from core.llm import build_flashcards, build_quiz
from schemas.models import FlashcardRequest, QuizRequest

router = APIRouter(tags=["study"])


@router.post("/quiz")
def quiz(payload: QuizRequest):
    try:
        return build_quiz(topic=payload.topic, num_questions=payload.num_questions)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/flashcards")
def flashcards(payload: FlashcardRequest):
    try:
        return build_flashcards(topic=payload.topic, count=payload.count)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
