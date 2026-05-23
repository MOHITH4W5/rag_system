import json

import requests

from app.config import LLM_MODEL, OLLAMA_BASE_URL


def query_llm(prompt: str, stream: bool = False) -> str:
    """Send a prompt to locally running Ollama."""
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": stream,
        "options": {
            "temperature": 0.1,
            "top_p": 0.9,
            "num_ctx": 4096,
        },
    }

    try:
        if stream:
            return _stream_response(url, payload)

        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get("response", "")

    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to Ollama. Is it running? Run: `ollama serve`"
    except requests.exceptions.Timeout:
        return "Error: LLM request timed out. Try a shorter prompt."
    except Exception as exc:
        return f"Error: {str(exc)}"


def _stream_response(url: str, payload: dict):
    """Yield response tokens one-by-one for streaming UIs."""
    with requests.post(url, json=payload, stream=True, timeout=120) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                token = chunk.get("response", "")
                yield token
                if chunk.get("done"):
                    break


def build_rag_prompt(question: str, context: str) -> str:
    """Build the full prompt sent to LLM."""
    return f"""You are a helpful assistant that answers questions based ONLY on the provided context.

Rules:
- Answer only from the context below. Do not use outside knowledge.
- If the answer is not in the context, say: "I don't have enough information to answer this."
- Be concise and direct. Cite the source when helpful.
- Do not make up information.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:"""


def check_ollama_health() -> bool:
    """Check if Ollama is running and model is available."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = [m["name"] for m in response.json().get("models", [])]
            if any(LLM_MODEL in m for m in models):
                print(f"[LLM] Ollama running. Model '{LLM_MODEL}' is available.")
                return True

            print(f"[LLM] Ollama running but model '{LLM_MODEL}' not found.")
            print(f"[LLM] Available models: {models}")
            print(f"[LLM] Run: ollama pull {LLM_MODEL}")
            return False
    except Exception:
        print("[LLM] Ollama is not running. Run: ollama serve")
        return False

    return False
