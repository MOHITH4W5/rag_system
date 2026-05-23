# Quick Start Guide

## Prerequisites

1. **PostgreSQL** installed and running
2. **Python 3.8+** installed
3. **Ollama** installed

## Step-by-Step Setup

### 1. Database Setup

```bash
# Create database
psql -U postgres
CREATE DATABASE rag_db;
\q

# Run schema
psql -U postgres -d rag_db -f schema.sql
```

### 2. Install Ollama & LLaMA-3

```bash
# Linux/Mac
curl -fsSL https://ollama.ai/install.sh | sh

# Windows: Download from https://ollama.ai/download

# Pull model
ollama pull llama3

# Start server (in separate terminal)
ollama serve
```

### 3. Python Environment

```bash
cd rag_system

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment

Edit `.env` file:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rag_db
DB_USER=postgres
DB_PASSWORD=YOUR_PASSWORD_HERE
```

### 5. Test Components

```bash
# Test embeddings
python tests/test_embeddings.py

# Test vector store
python tests/test_vector_store.py

# Test database connection
python -c "from app.database import test_connection; test_connection()"
```

### 6. Run Application

```bash
streamlit run app/ui.py
```

Open browser to `http://localhost:8501`

## Usage Flow

1. **Upload Document**
   - Click "Browse files" in sidebar
   - Select PDF/TXT/DOCX
   - Click "Process Document"
   - Wait for embedding completion

2. **Ask Questions**
   - Type question in chat input
   - Press Enter
   - View answer and sources

3. **Review Sources**
   - Click "📎 Sources" expander
   - See which documents were used
   - Check relevance scores

## Troubleshooting

### "Cannot connect to Ollama"
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve
```

### "Database connection failed"
```bash
# Test PostgreSQL
psql -U postgres -d rag_db -c "SELECT 1;"

# Check credentials in .env
```

### "No results found"
```bash
# Verify documents are embedded
python -c "from app.vector_store import FAISSVectorStore; print(FAISSVectorStore().get_total_vectors())"
```

## Performance Tips

- **First run is slow:** Model downloads (~500MB)
- **Batch uploads:** Process multiple docs at once
- **GPU acceleration:** Use `faiss-gpu` for large datasets
- **Context window:** Adjust `num_ctx` in `app/llm.py` for longer contexts

## Next Steps

- Add more documents to build knowledge base
- Experiment with different questions
- Check query logs in database for analytics
- Customize chunk size in `app/ingestion.py`
- Adjust retrieval parameters in `app/config.py`
