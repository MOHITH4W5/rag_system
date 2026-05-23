from app.config import RAG_ENGINE, VALID_RAG_ENGINES

_runtime_engine = RAG_ENGINE if RAG_ENGINE in VALID_RAG_ENGINES else "langchain"


def get_engine() -> str:
    return _runtime_engine


def set_engine(engine: str) -> str:
    global _runtime_engine
    normalized = engine.strip().lower()
    if normalized not in VALID_RAG_ENGINES:
        raise ValueError(f"Invalid engine '{engine}'. Must be one of {sorted(VALID_RAG_ENGINES)}")
    _runtime_engine = normalized
    return _runtime_engine
