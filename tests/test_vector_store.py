# tests/test_vector_store.py
import numpy as np
from app.embeddings import generate_embedding, generate_embeddings_batch
from app.vector_store import FAISSVectorStore

def test_add_and_search():
    store = FAISSVectorStore()
    
    texts = [
        "Python is a programming language",
        "Machine learning uses neural networks",
        "The weather is sunny today",
        "Deep learning is a subset of ML",
        "I enjoy cooking pasta",
    ]
    chunk_ids = [101, 102, 103, 104, 105]
    
    embeddings = generate_embeddings_batch(texts)
    store.add_embeddings(embeddings, chunk_ids)
    
    query_vec = generate_embedding("What is deep learning?")
    results = store.search(query_vec, top_k=3)
    
    print("Search results:")
    for r in results:
        print(f"  chunk_id={r['chunk_id']}, score={r['score']:.4f}")
    
    assert results[0]["chunk_id"] == 104, "Wrong top result!"
    print("✅ FAISS add and search passed")

if __name__ == "__main__":
    test_add_and_search()
