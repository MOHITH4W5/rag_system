# tests/test_retrieval.py
from app.retrieval import retrieve_relevant_chunks, format_context

def test_retrieval():
    query = "What is the main topic discussed?"
    chunks = retrieve_relevant_chunks(query, top_k=3)
    
    print(f"Retrieved {len(chunks)} chunks")
    for chunk in chunks:
        print(f"  Score: {chunk['relevance_score']:.4f} | Source: {chunk['filename']}")
        print(f"  Text preview: {chunk['chunk_text'][:100]}...")
    
    context = format_context(chunks)
    print("\nFormatted context preview:")
    print(context[:500])
    print("✅ Retrieval test passed")

if __name__ == "__main__":
    test_retrieval()
