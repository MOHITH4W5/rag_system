from typing import Literal

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    use_web: bool = False


class EngineRequest(BaseModel):
    engine: Literal["langchain", "classic"]


class WebSearchRequest(BaseModel):
    query: str
    max_results: int = Field(default=5, ge=1, le=10)


class QuizRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=240)
    num_questions: int = Field(default=5, ge=3, le=10)


class MindMapRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=240)
    max_nodes: int = Field(default=12, ge=5, le=20)


class FlashcardRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=240)
    count: int = Field(default=8, ge=4, le=20)


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=3, max_length=200)
