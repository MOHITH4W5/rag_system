# tests/test_pipeline.py
from app.pipeline import ask
from app.llm import check_ollama_health

def test_full_pipeline():
    if not check_ollama_health():
        print("⚠️ Skipping LLM test — Ollama not running")
        return

    result = ask("What is this document about?")
    
    print(f"Question: {result['question']}")
    print(f"Answer: {result['answer']}")
    print(f"Sources: {result['sources']}")
    print(f"Response time: {result['response_time_ms']}ms")
    
    assert "answer" in result
    assert len(result["answer"]) > 0
    print("✅ Full pipeline test passed")

if __name__ == "__main__":
    test_full_pipeline()
