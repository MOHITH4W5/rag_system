"""
Simple RAG Demo - No Database Required
This demonstrates the core RAG functionality without needing PostgreSQL setup.
"""

print("=" * 60)
print("RAG System - Standalone Demo")
print("=" * 60)

# Step 1: Install minimal dependencies
print("\n[1/6] Checking dependencies...")
import subprocess
import sys

required = ['sentence-transformers', 'faiss-cpu', 'numpy', 'requests']
for package in required:
    try:
        __import__(package.replace('-', '_'))
        print(f"  [OK] {package} installed")
    except ImportError:
        print(f"  Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
        print(f"  [OK] {package} installed")

print("\n[2/6] Loading embedding model...")
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import requests
import json

model = SentenceTransformer('all-MiniLM-L6-v2')
print("  [OK] Model loaded (384 dimensions)")

# Step 2: Create sample documents
print("\n[3/6] Creating sample documents...")
documents = [
    {
        "id": 1,
        "title": "Machine Learning Basics",
        "text": "Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed. It uses algorithms to identify patterns and make predictions."
    },
    {
        "id": 2,
        "title": "Deep Learning",
        "text": "Deep learning is a specialized branch of machine learning that uses neural networks with multiple layers. It excels at tasks like image recognition, natural language processing, and speech recognition."
    },
    {
        "id": 3,
        "title": "Natural Language Processing",
        "text": "Natural Language Processing (NLP) is a field of AI that focuses on the interaction between computers and human language. It enables machines to understand, interpret, and generate human language."
    },
    {
        "id": 4,
        "title": "Computer Vision",
        "text": "Computer vision is an AI field that trains computers to interpret and understand visual information from the world. It powers applications like facial recognition, autonomous vehicles, and medical image analysis."
    },
    {
        "id": 5,
        "title": "Reinforcement Learning",
        "text": "Reinforcement learning is a type of machine learning where an agent learns to make decisions by interacting with an environment. It receives rewards or penalties based on its actions and learns to maximize cumulative rewards."
    }
]

print(f"  [OK] Created {len(documents)} sample documents")

# Step 3: Generate embeddings
print("\n[4/6] Generating embeddings...")
texts = [doc["text"] for doc in documents]
embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
embeddings = embeddings.astype(np.float32)
print(f"  [OK] Generated {len(embeddings)} embeddings")

# Step 4: Create FAISS index
print("\n[5/6] Building FAISS index...")
dimension = embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity

# Normalize for cosine similarity
faiss.normalize_L2(embeddings)
index.add(embeddings)
print(f"  [OK] FAISS index created with {index.ntotal} vectors")

# Step 5: Check Ollama
print("\n[6/6] Checking Ollama status...")
ollama_available = False
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=2)
    if response.status_code == 200:
        models = [m["name"] for m in response.json().get("models", [])]
        if any("llama3" in m for m in models):
            print("  [OK] Ollama running with llama3")
            ollama_available = True
        else:
            print("  [WARNING] Ollama running but llama3 not found")
            print(f"    Available models: {models}")
    else:
        print("  [WARNING] Ollama not responding")
except:
    print("  [WARNING] Ollama not running (answers will be context-only)")

print("\n" + "=" * 60)
print("Setup Complete! Ready for queries.")
print("=" * 60)

# Query function
def search_documents(query, top_k=3):
    """Search for relevant documents"""
    query_embedding = model.encode([query], convert_to_numpy=True).astype(np.float32)
    faiss.normalize_L2(query_embedding)
    
    scores, indices = index.search(query_embedding, top_k)
    
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx != -1:
            results.append({
                "document": documents[idx],
                "score": float(score)
            })
    return results

def query_llm(prompt):
    """Query Ollama LLM"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1}
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get("response", "")
    except:
        pass
    return None

def ask_question(question):
    """Full RAG pipeline"""
    print(f"\n{'='*60}")
    print(f"Question: {question}")
    print(f"{'='*60}")
    
    # Retrieve relevant documents
    print("\n[Retrieval] Searching for relevant documents...")
    results = search_documents(question, top_k=3)
    
    print(f"Found {len(results)} relevant documents:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['document']['title']} (score: {result['score']:.4f})")
        print(f"   {result['document']['text'][:100]}...")
    
    # Build context
    context = "\n\n".join([
        f"[Source: {r['document']['title']}]\n{r['document']['text']}"
        for r in results
    ])
    
    # Query LLM if available
    if ollama_available:
        print("\n[LLM] Generating answer...")
        prompt = f"""You are a helpful assistant. Answer the question based ONLY on the provided context.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:"""
        
        answer = query_llm(prompt)
        if answer:
            print(f"\n{'='*60}")
            print("Answer:")
            print(f"{'='*60}")
            print(answer)
        else:
            print("\n[WARNING] LLM request failed. Showing context only.")
    else:
        print("\n[Info] Ollama not available. Showing retrieved context only.")
    
    print(f"\n{'='*60}\n")

# Interactive demo
print("\n" + "=" * 60)
print("Demo Queries")
print("=" * 60)

# Run example queries
example_questions = [
    "What is machine learning?",
    "Tell me about neural networks",
    "How does reinforcement learning work?"
]

print("\nRunning example queries...\n")
for question in example_questions:
    ask_question(question)
    input("Press Enter to continue...")

# Interactive mode
print("\n" + "=" * 60)
print("Interactive Mode")
print("=" * 60)
print("Type your questions (or 'quit' to exit)\n")

while True:
    try:
        question = input("\nYour question: ").strip()
        if question.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break
        if question:
            ask_question(question)
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        break
    except Exception as e:
        print(f"\nError: {e}")
