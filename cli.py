#!/usr/bin/env python
# cli.py - Command line interface for RAG system

import sys
from app.pipeline import ask
from app.llm import check_ollama_health
from app.database import test_connection, get_all_documents
from app.vector_store import FAISSVectorStore


def main():
    if len(sys.argv) < 2:
        print("RAG System CLI")
        print("\nUsage:")
        print("  python cli.py status          - Check system status")
        print("  python cli.py list            - List all documents")
        print("  python cli.py ask 'question'  - Ask a question")
        print("  python cli.py stats           - Show statistics")
        return

    command = sys.argv[1]

    if command == "status":
        print("=== System Status ===")
        print("\n1. Database:")
        test_connection()
        
        print("\n2. LLM (Ollama):")
        check_ollama_health()
        
        print("\n3. Vector Store:")
        store = FAISSVectorStore()
        print(f"   Total vectors: {store.get_total_vectors()}")

    elif command == "list":
        print("=== Documents ===")
        docs = get_all_documents()
        if not docs:
            print("No documents found.")
        else:
            for doc in docs:
                print(f"ID: {doc[0]} | {doc[1]} | Type: {doc[2]} | Uploaded: {doc[3]}")

    elif command == "ask":
        if len(sys.argv) < 3:
            print("Error: Please provide a question")
            print("Usage: python cli.py ask 'your question here'")
            return
        
        question = " ".join(sys.argv[2:])
        print(f"\nQuestion: {question}\n")
        
        result = ask(question)
        
        print(f"Answer: {result['answer']}\n")
        
        if result['sources']:
            print("Sources:")
            for s in result['sources']:
                print(f"  - {s['filename']} (score: {s['relevance_score']})")
        
        print(f"\nResponse time: {result['response_time_ms']}ms")

    elif command == "stats":
        print("=== Statistics ===")
        
        from app.database import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM documents")
        doc_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM document_chunks")
        chunk_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM embeddings_metadata")
        embedded_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM query_logs")
        query_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"Documents: {doc_count}")
        print(f"Chunks: {chunk_count}")
        print(f"Embedded: {embedded_count}")
        print(f"Queries logged: {query_count}")
        
        store = FAISSVectorStore()
        print(f"FAISS vectors: {store.get_total_vectors()}")

    else:
        print(f"Unknown command: {command}")
        print("Run 'python cli.py' for usage")


if __name__ == "__main__":
    main()
