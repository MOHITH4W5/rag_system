from datetime import datetime

from app.embeddings import generate_embedding
from app.embeddings_manager import get_chunks_by_ids
from app.llm import build_rag_prompt, query_llm
from app.vector_store import FAISSVectorStore
from core.data_access import get_accessible_document_ids, log_user_query


def _retrieve_authorized_chunks(question: str, top_k: int, accessible_doc_ids: set[int]) -> tuple[list[dict], list[int]]:
    if not accessible_doc_ids:
        return [], []

    query_embedding = generate_embedding(question)
    store = FAISSVectorStore()

    multipliers = [2, 4, 6]
    selected_chunks: list[dict] = []
    selected_chunk_ids: list[int] = []

    for multiplier in multipliers:
        raw = store.search(query_embedding, top_k=top_k * multiplier)
        if not raw:
            break
        chunk_ids = [item["chunk_id"] for item in raw]
        chunks = get_chunks_by_ids(chunk_ids, allowed_document_ids=accessible_doc_ids)
        if not chunks:
            continue

        by_id = {chunk["chunk_id"]: chunk for chunk in chunks}
        score_map = {item["chunk_id"]: item["score"] for item in raw}

        filtered = []
        for cid in chunk_ids:
            if cid not in by_id:
                continue
            chunk = by_id[cid]
            chunk["relevance_score"] = float(score_map.get(cid, 0.0))
            filtered.append(chunk)

        if filtered:
            selected_chunks = filtered[:top_k]
            selected_chunk_ids = [chunk["chunk_id"] for chunk in selected_chunks]
            break

    return selected_chunks, selected_chunk_ids


def _format_context(chunks: list[dict]) -> str:
    if not chunks:
        return "No relevant context found."
    parts = []
    for idx, chunk in enumerate(chunks, 1):
        source = chunk.get("filename") or chunk.get("title") or "Unknown"
        parts.append(f"[Source {idx}: {source}]\n{chunk['chunk_text']}")
    return "\n\n---\n\n".join(parts)


def _ask_with_langchain(question: str, context: str) -> str:
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_ollama import ChatOllama

    from app.config import LLM_MODEL, OLLAMA_BASE_URL

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Answer only from provided context. If context is insufficient, say you don't have enough information.",
            ),
            ("human", "CONTEXT:\n{context}\n\nQUESTION:\n{question}\n\nANSWER:"),
        ]
    )
    chain = prompt | ChatOllama(model=LLM_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.1) | StrOutputParser()
    return chain.invoke({"context": context, "question": question})


def run_query(question: str, top_k: int, engine: str, current_user: dict):
    start = datetime.now()
    accessible_doc_ids = get_accessible_document_ids(current_user["id"], current_user["role"])
    chunks, chunk_ids = _retrieve_authorized_chunks(question, top_k, accessible_doc_ids)

    if not chunks:
        answer = "No relevant documents found for your account. Upload docs or ask admin for global sources."
        payload = {
            "question": question,
            "answer": answer,
            "sources": [],
            "response_time_ms": 0,
            "engine_used": engine,
        }
        log_user_query(current_user["id"], question, answer, [], 0)
        return payload

    context = _format_context(chunks)
    if engine == "langchain":
        answer = _ask_with_langchain(question, context)
        engine_used = "langchain"
    else:
        answer = query_llm(build_rag_prompt(question, context))
        engine_used = "classic"

    elapsed_ms = int((datetime.now() - start).total_seconds() * 1000)
    log_user_query(current_user["id"], question, answer, chunk_ids, elapsed_ms)

    seen = set()
    sources = []
    for chunk in chunks:
        fname = chunk.get("filename", "Unknown")
        if fname in seen:
            continue
        seen.add(fname)
        sources.append(
            {
                "filename": fname,
                "document_id": chunk["document_id"],
                "relevance_score": round(float(chunk.get("relevance_score", 0.0)), 4),
            }
        )

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "response_time_ms": elapsed_ms,
        "engine_used": engine_used,
    }


def retrieve_context_for_user(topic: str, current_user: dict, top_k: int = 8) -> str:
    accessible_doc_ids = get_accessible_document_ids(current_user["id"], current_user["role"])
    chunks, _ = _retrieve_authorized_chunks(topic, top_k, accessible_doc_ids)
    return _format_context(chunks) if chunks else "No local context."
