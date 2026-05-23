# app/config.py
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

# PostgreSQL
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "rag_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password")

DATABASE_URL = f"postgresql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Embeddings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# FAISS
FAISS_INDEX_PATH = "data/faiss_index/index.faiss"
FAISS_ID_MAP_PATH = "data/faiss_index/id_map.json"

# Ollama / LLM
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3")

# RAG engine options: "langchain" | "classic"
RAG_ENGINE = os.getenv("RAG_ENGINE", "langchain").strip().lower()
VALID_RAG_ENGINES = {"langchain", "classic"}

# Retrieval
TOP_K_RESULTS = 5
