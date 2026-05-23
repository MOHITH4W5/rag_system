# RAG System - Technical Architecture

## System Overview

This is a production-ready Retrieval-Augmented Generation (RAG) system that enables semantic search and question-answering over document collections using 100% local infrastructure.

## Core Components

### 1. Document Ingestion Pipeline
**File:** `app/ingestion.py`

- Supports PDF, DOCX, TXT formats
- Extracts text using PyPDF2 and python-docx
- Chunks text with configurable size and overlap
- Stores metadata and chunks in PostgreSQL

### 2. Embedding Generation
**File:** `app/embeddings.py`

- Uses Sentence Transformers (all-MiniLM-L6-v2)
- 384-dimensional embeddings
- Batch processing for efficiency
- Float32 precision for FAISS compatibility

### 3. Vector Storage
**File:** `app/vector_store.py`

- FAISS IndexFlatIP for exact cosine similarity
- L2 normalization for proper similarity scoring
- Persistent storage with JSON ID mapping
- Supports deletion via index rebuilding

### 4. Embeddings Orchestration
**File:** `app/embeddings_manager.py`

- Coordinates DB ↔ FAISS operations
- Tracks embedding status in PostgreSQL
- Batch processes unembedded chunks
- Retrieves chunks by ID for context building

### 5. Semantic Retrieval
**File:** `app/retrieval.py`

- Embeds user queries
- Searches FAISS for top-K similar chunks
- Fetches full chunk data from PostgreSQL
- Formats context for LLM consumption

### 6. LLM Integration
**File:** `app/llm.py`

- Connects to local Ollama server
- Uses LLaMA-3 model
- Supports streaming responses
- Implements RAG-specific prompting
- Health checks and error handling

### 7. Query Pipeline
**File:** `app/pipeline.py`

- End-to-end query orchestration
- Logs all queries for analytics
- Tracks response times
- Returns structured results with sources

### 8. User Interface
**File:** `app/ui.py`

- Streamlit-based chat interface
- Document upload and processing
- Real-time status indicators
- Source attribution display

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     INGESTION PHASE                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    [Upload Document]
                            │
                            ▼
                  [Extract Text by Type]
                            │
                            ▼
                    [Chunk with Overlap]
                            │
                            ▼
                  [Save to PostgreSQL]
                            │
                            ▼
              [Generate Embeddings (Batch)]
                            │
                            ▼
                [Store Vectors in FAISS]
                            │
                            ▼
            [Mark as Embedded in PostgreSQL]

┌─────────────────────────────────────────────────────────────┐
│                      QUERY PHASE                            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    [User Question]
                            │
                            ▼
                  [Embed Question Vector]
                            │
                            ▼
              [FAISS Similarity Search]
                            │
                            ▼
            [Get Top-K Chunk IDs + Scores]
                            │
                            ▼
          [Fetch Chunk Text from PostgreSQL]
                            │
                            ▼
              [Format Context with Sources]
                            │
                            ▼
            [Build RAG Prompt (System + Context + Question)]
                            │
                            ▼
                  [Send to Ollama LLM]
                            │
                            ▼
                    [Receive Answer]
                            │
                            ▼
              [Log Query to PostgreSQL]
                            │
                            ▼
          [Return Answer + Sources + Metadata]
```

## Database Schema

### documents
- Stores document metadata
- Links to chunks via foreign key

### document_chunks
- Stores text chunks with position info
- Enables context reconstruction

### embeddings_metadata
- Tracks which chunks are embedded
- Records model version for reproducibility

### query_logs
- Audit trail for all queries
- Enables analytics and fine-tuning
- Stores retrieved chunk IDs for debugging

## Key Design Decisions

### Why FAISS?
- **Speed:** Sub-millisecond search on 100K+ vectors
- **Accuracy:** IndexFlatIP provides exact cosine similarity
- **Privacy:** 100% local, no cloud dependencies
- **Cost:** Zero ongoing costs

### Why Sentence Transformers?
- **Quality:** State-of-the-art semantic embeddings
- **Speed:** Fast inference on CPU
- **Size:** Compact models (90MB)
- **Compatibility:** Works with FAISS out of the box

### Why Ollama + LLaMA-3?
- **Local:** No API keys or rate limits
- **Free:** No per-token costs
- **Private:** Data never leaves machine
- **Powerful:** 8B parameter model with strong reasoning

### Why PostgreSQL?
- **Reliability:** ACID compliance
- **Flexibility:** Rich querying capabilities
- **Integration:** Easy to add analytics
- **Familiarity:** Industry standard

## Performance Characteristics

### Embedding Generation
- **Speed:** ~100 chunks/second (batch mode)
- **Memory:** ~500MB for model
- **Bottleneck:** CPU-bound

### Vector Search
- **Latency:** <10ms for 10K vectors
- **Scaling:** Linear with index size
- **Memory:** ~1.5KB per vector

### LLM Inference
- **Latency:** 2-5 seconds typical
- **Throughput:** ~50 tokens/second
- **Memory:** ~8GB for LLaMA-3 8B

### End-to-End Query
- **Total time:** 3-7 seconds
- **Breakdown:**
  - Embedding: 50ms
  - Search: 10ms
  - DB fetch: 20ms
  - LLM: 2-5s

## Scalability Considerations

### Current Limits
- **Documents:** 1000s
- **Chunks:** 100K+
- **Concurrent users:** 1-5

### Scaling Strategies
1. **More documents:** Use FAISS IVF index for 1M+ vectors
2. **More users:** Add Redis caching layer
3. **Faster inference:** Use GPU for embeddings + LLM
4. **Better quality:** Add re-ranking with cross-encoders

## Security & Privacy

- ✅ No data sent to external APIs
- ✅ All processing happens locally
- ✅ Database credentials in .env (not committed)
- ✅ No hardcoded secrets
- ⚠️ No authentication (add for production)
- ⚠️ No input sanitization (add for production)

## Testing Strategy

### Unit Tests
- `test_embeddings.py`: Vector generation and similarity
- `test_vector_store.py`: FAISS operations
- `test_retrieval.py`: Search pipeline
- `test_pipeline.py`: End-to-end flow

### Integration Tests
- Database connectivity
- Ollama health checks
- File upload and processing

### Manual Testing
- Use CLI tool for quick checks
- Streamlit UI for user experience

## Monitoring & Observability

### Built-in Logging
- Console logs for all operations
- Query logs in database
- Response time tracking

### Metrics to Track
- Average response time
- Retrieval accuracy (manual review)
- Most common queries
- Document usage patterns

## Future Enhancements

### High Priority
- [ ] Hybrid search (BM25 + semantic)
- [ ] Document filtering by metadata
- [ ] Multi-turn conversations with memory

### Medium Priority
- [ ] Re-ranking with cross-encoders
- [ ] Automatic chunk size optimization
- [ ] Export/import functionality

### Low Priority
- [ ] Multi-language support
- [ ] OCR for scanned documents
- [ ] Graph-based retrieval

## Deployment Options

### Local Development
```bash
streamlit run app/ui.py
```

### Docker (Future)
```dockerfile
FROM python:3.10
# Install dependencies
# Run Streamlit
```

### Production Considerations
- Add authentication (OAuth, JWT)
- Use production WSGI server
- Add rate limiting
- Implement caching
- Set up monitoring (Prometheus)
- Add backup strategy

## Maintenance

### Regular Tasks
- Monitor disk usage (FAISS index grows)
- Review query logs for improvements
- Update models periodically
- Backup PostgreSQL database

### Troubleshooting
- Check logs in console output
- Verify Ollama is running
- Test database connection
- Inspect FAISS index size

## Contributing

This is a portfolio project demonstrating:
- End-to-end RAG implementation
- Production-ready code structure
- Comprehensive documentation
- Testing best practices
- Scalable architecture

## License

MIT License - Free for personal and commercial use
