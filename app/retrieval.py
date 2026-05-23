# app/retrieval.py
from app.embeddings import generate_embedding
from app.vector_store import FAISSVectorStore
from app.embeddings_manager import get_chunks_by_ids
from app.config import TOP_K_RESULTS


def retrieve_relevant_chunks(query: str, top_k: int = TOP_K_RESULTS) -> list[dict]:
    """Given a user question, find the most relevant document chunks."""
    print(f"[Retrieval] Searching for: '{query[:80]}...'")

    query_embedding = generate_embedding(query)

    store = FAISSVectorStore()
    faiss_results = store.search(query_embedding, top_k=top_k)

    if not faiss_results:
        print("[Retrieval] No results found in vector store.")
        return []

    chunk_ids = [r["chunk_id"] for r in faiss_results]
    chunks = get_chunks_by_ids(chunk_ids)

    score_map = {r["chunk_id"]: r["score"] for r in faiss_results}
    for chunk in chunks:
        chunk["relevance_score"] = score_map.get(chunk["chunk_id"], 0.0)

    chunks.sort(key=lambda x: x["relevance_score"], reverse=True)

    print(f"[Retrieval] Found {len(chunks)} relevant chunks")
    return chunks


def format_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a clean context string for the LLM."""
    if not chunks:
        return "No relevant context found."

    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk.get("filename") or chunk.get("title") or "Unknown"
        context_parts.append(
            f"[Source {i}: {source}]\n{chunk['chunk_text']}"
        )

    return "\n\n---\n\n".join(context_parts)
