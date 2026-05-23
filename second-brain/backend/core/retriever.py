def run_query(question: str, top_k: int, engine: str):
    from app.pipeline import ask

    return ask(question=question, top_k=top_k, engine=engine)
