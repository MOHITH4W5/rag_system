# RAG System - Command Cheat Sheet

## Setup Commands

### Database
```bash
# Create database
psql -U postgres -c "CREATE DATABASE rag_db;"

# Run schema
psql -U postgres -d rag_db -f schema.sql

# Connect to database
psql -U postgres -d rag_db
```

### Ollama
```bash
# Install (Linux/Mac)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull model
ollama pull llama3

# Start server
ollama serve

# List models
ollama list

# Test API
curl http://localhost:11434/api/tags
```

### Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Upgrade pip
pip install --upgrade pip
```

## Running the Application

### Streamlit UI
```bash
streamlit run app/ui.py
```

### CLI Tool
```bash
# Check system status
python cli.py status

# List documents
python cli.py list

# Ask a question
python cli.py ask "What is machine learning?"

# Show statistics
python cli.py stats
```

## Testing Commands

### Run All Tests
```bash
python tests/test_embeddings.py
python tests/test_vector_store.py
python tests/test_retrieval.py
python tests/test_pipeline.py
```

### Quick Tests
```bash
# Test database connection
python -c "from app.database import test_connection; test_connection()"

# Test Ollama
python -c "from app.llm import check_ollama_health; check_ollama_health()"

# Check FAISS index
python -c "from app.vector_store import FAISSVectorStore; print(f'Vectors: {FAISSVectorStore().get_total_vectors()}')"

# Test embedding
python -c "from app.embeddings import generate_embedding; print(generate_embedding('test').shape)"
```

## Database Queries

### Useful SQL Commands
```sql
-- Count documents
SELECT COUNT(*) FROM documents;

-- List all documents
SELECT id, filename, upload_date FROM documents ORDER BY upload_date DESC;

-- Count chunks per document
SELECT d.filename, COUNT(dc.id) as chunk_count
FROM documents d
LEFT JOIN document_chunks dc ON dc.document_id = d.id
GROUP BY d.id, d.filename;

-- Check embedding status
SELECT 
    d.filename,
    COUNT(dc.id) as total_chunks,
    COUNT(em.id) as embedded_chunks
FROM documents d
LEFT JOIN document_chunks dc ON dc.document_id = d.id
LEFT JOIN embeddings_metadata em ON em.chunk_id = dc.id
GROUP BY d.id, d.filename;

-- Recent queries
SELECT question, response_time_ms, created_at 
FROM query_logs 
ORDER BY created_at DESC 
LIMIT 10;

-- Average response time
SELECT AVG(response_time_ms) as avg_ms FROM query_logs;

-- Delete a document and all related data
DELETE FROM documents WHERE id = 1;
```

## Python Interactive Commands

### Start Python Shell
```bash
python
```

### Useful Snippets
```python
# Import modules
from app.embeddings import generate_embedding
from app.vector_store import FAISSVectorStore
from app.pipeline import ask
from app.database import get_all_documents

# Generate embedding
vec = generate_embedding("test text")
print(vec.shape)  # Should be (384,)

# Check vector store
store = FAISSVectorStore()
print(f"Total vectors: {store.get_total_vectors()}")

# Ask a question
result = ask("What is this about?")
print(result['answer'])

# List documents
docs = get_all_documents()
for doc in docs:
    print(doc)
```

## Troubleshooting Commands

### Check Ports
```bash
# Check if Ollama is running (port 11434)
netstat -an | grep 11434

# Check if PostgreSQL is running (port 5432)
netstat -an | grep 5432

# Check if Streamlit is running (port 8501)
netstat -an | grep 8501
```

### Process Management
```bash
# Find Ollama process
ps aux | grep ollama

# Kill Ollama (if needed)
pkill ollama

# Find Python processes
ps aux | grep python

# Find Streamlit process
ps aux | grep streamlit
```

### Logs and Debugging
```bash
# Run with verbose output
python -u app/ui.py

# Check Python version
python --version

# Check installed packages
pip list

# Check specific package
pip show sentence-transformers
```

## File Operations

### Backup
```bash
# Backup database
pg_dump -U postgres rag_db > backup.sql

# Backup FAISS index
cp -r data/faiss_index data/faiss_index_backup

# Backup .env
cp .env .env.backup
```

### Restore
```bash
# Restore database
psql -U postgres rag_db < backup.sql

# Restore FAISS index
cp -r data/faiss_index_backup data/faiss_index
```

### Clean Up
```bash
# Remove FAISS index (start fresh)
rm -rf data/faiss_index/*

# Remove uploaded files
rm -rf data/uploads/*

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

## Development Commands

### Code Quality
```bash
# Format code (if black installed)
black app/ tests/

# Lint code (if pylint installed)
pylint app/

# Type checking (if mypy installed)
mypy app/
```

### Git Commands
```bash
# Initialize repo
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: RAG system"

# Create GitHub repo and push
git remote add origin https://github.com/yourusername/rag-system.git
git branch -M main
git push -u origin main
```

## Performance Monitoring

### System Resources
```bash
# Check memory usage
free -h

# Check disk usage
df -h

# Monitor CPU
top

# Monitor specific process
top -p $(pgrep -f streamlit)
```

### Application Metrics
```python
# In Python shell
from app.database import get_connection

conn = get_connection()
cursor = conn.cursor()

# Query performance stats
cursor.execute("""
    SELECT 
        COUNT(*) as total_queries,
        AVG(response_time_ms) as avg_time,
        MIN(response_time_ms) as min_time,
        MAX(response_time_ms) as max_time
    FROM query_logs
""")
print(cursor.fetchone())
```

## Quick Reference

### Default Ports
- PostgreSQL: 5432
- Ollama: 11434
- Streamlit: 8501

### Default Paths
- Config: `app/config.py`
- FAISS Index: `data/faiss_index/`
- Uploads: `data/uploads/`
- Logs: Console output

### Environment Variables
- DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
- See `.env` file for all options

### Key Files
- `app/pipeline.py` - Main query logic
- `app/embeddings.py` - Vector generation
- `app/vector_store.py` - FAISS operations
- `app/ui.py` - Streamlit interface
- `cli.py` - Command line tool
