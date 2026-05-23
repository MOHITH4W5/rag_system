from datetime import datetime

from app.config import LLM_MODEL, OLLAMA_BASE_URL, TOP_K_RESULTS
from app.retrieval import format_context, retrieve_relevant_chunks


def _build_chain():
    # Imported lazily so non-langchain mode still runs even if deps are missing.
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_ollama import ChatOllama

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a helpful assistant that answers questions based ONLY on the provided context.\n"
                "Rules:\n"
                "- Answer only from the context below. Do not use outside knowledge.\n"
                "- If the answer is not in the context, say: \"I don't have enough information to answer this.\"\n"
                "- Be concise and direct. Cite source filenames when helpful.\n"
                "- Do not make up information.""",
            ),
            (
                "human",
                "CONTEXT:\n{context}\n\nQUESTION:\n{question}\n\nANSWER:",
            ),
        ]
    )

    llm = ChatOllama(
        model=LLM_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.1,
    )

    return prompt | llm | StrOutputParser()


def ask_with_langchain(
    question: str,
    top_k: int = TOP_K_RESULTS,
) -> tuple[dict, list[int]]:
    """
    LangChain-backed RAG answer.

    Returns:
      payload dict compatible with existing API
      retrieved chunk_ids list (for query logging)
    """
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
    chain = _build_chain()
    answer = chain.invoke({"context": context, "question": question})

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
            "engine_used": "langchain",
        },
        chunk_ids,
    )
