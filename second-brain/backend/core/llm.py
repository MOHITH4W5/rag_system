import requests
import os
import json

from app.llm import query_llm


def _safe_json_loads(payload: str):
    try:
        return json.loads(payload)
    except Exception:
        return None


def web_search(query: str, max_results: int = 5):
    tavily_key = os.getenv("TAVILY_API_KEY", "").strip()
    if tavily_key:
        try:
            response = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": tavily_key,
                    "query": query,
                    "max_results": max_results,
                    "search_depth": "basic",
                },
                timeout=25,
            )
            response.raise_for_status()
            data = response.json()
            return {
                "query": query,
                "provider": "tavily",
                "results": [
                    {
                        "title": item.get("title", "Untitled"),
                        "url": item.get("url", ""),
                        "snippet": item.get("content", ""),
                    }
                    for item in data.get("results", [])
                ],
            }
        except Exception as exc:
            return {"query": query, "provider": "tavily", "results": [], "error": str(exc)}

    # Graceful local fallback keeps API contract stable for demos without keys.
    return {
        "query": query,
        "provider": "mock",
        "results": [
            {
                "title": "Web search integration placeholder",
                "url": "https://example.com",
                "snippet": "Set TAVILY_API_KEY to enable real live web search results.",
            }
        ][:max_results],
    }


def build_quiz(topic: str, num_questions: int):
    from app.retrieval import format_context, retrieve_relevant_chunks

    chunks = retrieve_relevant_chunks(topic, top_k=8)
    context = format_context(chunks) if chunks else "No local context."
    prompt = f"""Create {num_questions} high-quality quiz questions from the context below.
Return STRICT JSON with this shape:
{{
  "questions": [
    {{
      "type": "mcq" | "short",
      "question": "text",
      "options": ["A", "B", "C", "D"],
      "answer": "correct answer",
      "explanation": "short explanation"
    }}
  ]
}}

Topic: {topic}
Context:
{context}
"""
    raw = query_llm(prompt)
    parsed = _safe_json_loads(raw)
    if parsed and isinstance(parsed.get("questions"), list):
        return parsed
    return {"questions": [], "raw": raw}


def build_flashcards(topic: str, count: int):
    from app.retrieval import format_context, retrieve_relevant_chunks

    chunks = retrieve_relevant_chunks(topic, top_k=8)
    context = format_context(chunks) if chunks else "No local context."
    prompt = f"""Create {count} flashcards from the context.
Return STRICT JSON:
{{
  "flashcards": [
    {{"front": "question", "back": "answer"}}
  ]
}}

Topic: {topic}
Context:
{context}
"""
    raw = query_llm(prompt)
    parsed = _safe_json_loads(raw)
    if parsed and isinstance(parsed.get("flashcards"), list):
        return parsed
    return {"flashcards": [], "raw": raw}


def build_mindmap(topic: str, max_nodes: int):
    from app.retrieval import format_context, retrieve_relevant_chunks

    chunks = retrieve_relevant_chunks(topic, top_k=10)
    context = format_context(chunks) if chunks else "No local context."
    prompt = f"""Extract a compact concept graph for study.
Return STRICT JSON:
{{
  "nodes": [{{"id": "n1", "label": "concept"}}],
  "edges": [{{"source": "n1", "target": "n2", "label": "relation"}}]
}}
Rules:
- Keep nodes <= {max_nodes}
- Node labels should be short and readable.
- Edges should express meaningful semantic relations.

Topic: {topic}
Context:
{context}
"""
    raw = query_llm(prompt)
    parsed = _safe_json_loads(raw)
    if parsed and isinstance(parsed.get("nodes"), list):
        return parsed

    return {
        "nodes": [{"id": "n1", "label": topic}, {"id": "n2", "label": "No structured output"}],
        "edges": [{"source": "n1", "target": "n2", "label": "fallback"}],
        "raw": raw,
    }
