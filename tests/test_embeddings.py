# tests/test_embeddings.py
import numpy as np
from app.embeddings import generate_embedding, generate_embeddings_batch

def test_single_embedding():
    text = "Machine learning is a subset of artificial intelligence."
    vec = generate_embedding(text)
    print(f"Shape: {vec.shape}")
    print(f"Type: {vec.dtype}")
    print(f"First 5 values: {vec[:5]}")
    assert vec.shape == (384,), "Wrong dimension!"
    print("✅ Single embedding passed")

def test_batch_embeddings():
    texts = ["Hello world", "Python is great", "FAISS stores vectors"]
    vecs = generate_embeddings_batch(texts)
    print(f"Batch shape: {vecs.shape}")
    assert vecs.shape == (3, 384), "Wrong batch shape!"
    print("✅ Batch embeddings passed")

def test_similarity():
    from numpy.linalg import norm
    v1 = generate_embedding("The cat sat on the mat")
    v2 = generate_embedding("A cat is sitting on a mat")
    v3 = generate_embedding("Stock market crashed today")
    
    sim_12 = np.dot(v1, v2) / (norm(v1) * norm(v2))
    sim_13 = np.dot(v1, v3) / (norm(v1) * norm(v3))
    
    print(f"Similar texts similarity: {sim_12:.3f}")
    print(f"Different texts similarity: {sim_13:.3f}")
    assert sim_12 > sim_13, "Similarity check failed!"
    print("✅ Similarity test passed")

if __name__ == "__main__":
    test_single_embedding()
    test_batch_embeddings()
    test_similarity()
