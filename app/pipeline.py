from datetime import datetime

from app.config import RAG_ENGINE, TOP_K_RESULTS, VALID_RAG_ENGINES
from app.database import get_db_connection
from app.llm import build_rag_prompt, query_llm
from app.retrieval import format_context, retrieve_relevant_chunks


def log_query(question: str, answer: str, retrieved_chunk_ids: list[int], response_time_ms: int):
    """Save each query and response for analytics."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO query_logs
                        (question, answer, retrieved_chunk_ids, response_time_ms, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    """,
                    (question, answer, retrieved_chunk_ids, response_time_ms),
                )
            conn.commit()
    except Exception as exc:
        print(f"[Pipeline] Warning: failed to log query: {exc}")


def _ask_classic(question: str, top_k: int = TOP_K_RESULTS) -> tuple[dict, list[int]]:
    """Original custom RAG implementation."""
    start_time = datetime.now()

    chunks = retrieve_relevant_chunks(question, top_k=top_k)
    if not chunks:
        return (
            {
                "question": question,
                "answer": "No relevant documents found. Please upload documents first.",
                "sources": [],
                "response_time_ms": 0,
            },
            [],
        )

    context = format_context(chunks)
    prompt = build_rag_prompt(question, context)
    answer = query_llm(prompt)

    elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)

    sources = []
    seen = set()
    for chunk in chunks:
        fname = chunk.get("filename", "Unknown")
        if fname in seen:
            continue
        sources.append(
            {
                "filename": fname,
                "document_id": chunk["document_id"],
                "relevance_score": round(chunk["relevance_score"], 4),
            }
        )
        seen.add(fname)

    chunk_ids = [c["chunk_id"] for c in chunks]

    return (
        {
            "question": question,
            "answer": answer,
            "sources": sources,
            "response_time_ms": elapsed_ms,
            "engine_used": "classic",
        },
        chunk_ids,
    )


def ask(question: str, top_k: int = TOP_K_RESULTS, engine: str | None = None) -> dict:
    """Main entry point: ask a question and return an answer payload."""
    active_engine = (engine or RAG_ENGINE).strip().lower()
    if active_engine not in VALID_RAG_ENGINES:
        active_engine = RAG_ENGINE

    if active_engine == "langchain":
        try:
            from app.langchain_rag import ask_with_langchain

            result, chunk_ids = ask_with_langchain(question, top_k=top_k)
            log_query(question, result["answer"], chunk_ids, result["response_time_ms"])
            print(f"[Pipeline] Answered via LangChain in {result['response_time_ms']}ms")
            return result
        except Exception as exc:
            print(f"[Pipeline] LangChain path failed, falling back to classic: {exc}")

    result, chunk_ids = _ask_classic(question, top_k=top_k)
    log_query(question, result["answer"], chunk_ids, result["response_time_ms"])
    print(f"[Pipeline] Answered via classic pipeline in {result['response_time_ms']}ms")
    return result


def ask_streaming(question: str, top_k: int = TOP_K_RESULTS):
    """Streaming version for token-by-token UIs (classic mode only)."""
    from app.llm import LLM_MODEL, OLLAMA_BASE_URL, _stream_response

    chunks = retrieve_relevant_chunks(question, top_k=top_k)
    if not chunks:
        yield "No relevant documents found. Please upload documents first."
        return

    context = format_context(chunks)
    prompt = build_rag_prompt(question, context)

    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": True,
        "options": {"temperature": 0.1},
    }

    yield from _stream_response(url, payload)
