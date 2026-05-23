# RAG System - Visual Architecture

## System Components Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                            │
│                                                                     │
│  ┌──────────────────────┐              ┌──────────────────────┐   │
│  │   Streamlit Web UI   │              │     CLI Tool         │   │
│  │   (app/ui.py)        │              │     (cli.py)         │   │
│  └──────────┬───────────┘              └──────────┬───────────┘   │
└─────────────┼──────────────────────────────────────┼───────────────┘
              │                                      │
              └──────────────────┬───────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        QUERY PIPELINE                               │
│                        (app/pipeline.py)                            │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  1. Receive Question                                        │  │
│  │  2. Retrieve Relevant Chunks                                │  │
│  │  3. Format Context                                          │  │
│  │  4. Query LLM                                               │  │
│  │  5. Log Query                                               │  │
│  │  6. Return Answer + Sources                                 │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
              │                                      │
              │                                      │
    ┌─────────▼─────────┐              ┌────────────▼──────────┐
    │                   │              │                       │
    │   RETRIEVAL       │              │    LLM INTEGRATION    │
    │ (app/retrieval.py)│              │    (app/llm.py)       │
    │                   │              │                       │
    └─────────┬─────────┘              └────────────┬──────────┘
              │                                     │
              │                                     │
    ┌─────────▼─────────┐                          │
    │                   │                          │
    │   EMBEDDINGS      │                          │
    │ (app/embeddings.py)│                         │
    │                   │                          │
    │  Sentence         │                          │
    │  Transformers     │                          │
    │  (384-dim)        │                          │
    │                   │                          │
    └─────────┬─────────┘                          │
              │                                     │
              │                                     │
    ┌─────────▼─────────┐              ┌───────────▼───────────┐
    │                   │              │                       │
    │  VECTOR STORE     │              │   OLLAMA SERVER       │
    │(app/vector_store.py)│            │   (localhost:11434)   │
    │                   │              │                       │
    │  FAISS IndexFlatIP│              │   LLaMA-3 Model       │
    │  Cosine Similarity│              │   (8B parameters)     │
    │                   │              │                       │
    └─────────┬─────────┘              └───────────────────────┘
              │
              │
    ┌─────────▼─────────┐
    │                   │
    │  EMBEDDINGS MGR   │
    │(app/embeddings_   │
    │    manager.py)    │
    │                   │
    └─────────┬─────────┘
              │
              │
┌─────────────▼─────────────────────────────────────────────────────┐
│                      POSTGRESQL DATABASE                          │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  documents   │  │document_chunks│ │ embeddings_  │          │
│  │              │  │              │  │  metadata    │          │
│  │ - id         │  │ - id         │  │              │          │
│  │ - filename   │  │ - document_id│  │ - chunk_id   │          │
│  │ - file_type  │  │ - chunk_text │  │ - model_name │          │
│  │ - upload_date│  │ - chunk_index│  │ - created_at │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  query_logs                                              │   │
│  │                                                          │   │
│  │  - id                                                    │   │
│  │  - question                                              │   │
│  │  - answer                                                │   │
│  │  - retrieved_chunk_ids                                   │   │
│  │  - response_time_ms                                      │   │
│  │  - created_at                                            │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────┘
```

## Data Flow - Document Ingestion

```
┌──────────────┐
│ User uploads │
│   document   │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│  INGESTION (app/ingestion.py)        │
│                                      │
│  1. Extract text (PDF/DOCX/TXT)     │
│  2. Split into chunks (500 words)   │
│  3. Save to PostgreSQL              │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  PostgreSQL: documents table         │
│  PostgreSQL: document_chunks table   │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  EMBEDDINGS MANAGER                  │
│  (app/embeddings_manager.py)         │
│                                      │
│  1. Fetch unembedded chunks         │
│  2. Generate embeddings (batch)     │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  EMBEDDINGS (app/embeddings.py)      │
│                                      │
│  Sentence Transformers               │
│  all-MiniLM-L6-v2                   │
│  Output: 384-dim vectors            │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  VECTOR STORE (app/vector_store.py)  │
│                                      │
│  1. Normalize vectors (L2)          │
│  2. Add to FAISS index              │
│  3. Map FAISS ID → chunk ID         │
│  4. Save to disk                    │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  PostgreSQL: embeddings_metadata     │
│  Mark chunks as embedded             │
└──────────────────────────────────────┘
```

## Data Flow - Query Processing

```
┌──────────────┐
│ User asks    │
│  question    │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│  PIPELINE (app/pipeline.py)          │
│  Start timer                         │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  RETRIEVAL (app/retrieval.py)        │
│  1. Embed question                   │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  EMBEDDINGS (app/embeddings.py)      │
│  Convert question → 384-dim vector   │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  VECTOR STORE (app/vector_store.py)  │
│  1. Normalize query vector           │
│  2. FAISS similarity search          │
│  3. Return top-K chunk IDs + scores  │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  EMBEDDINGS MANAGER                  │
│  Fetch chunk text from PostgreSQL    │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  RETRIEVAL (app/retrieval.py)        │
│  Format context with sources         │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  LLM (app/llm.py)                    │
│  1. Build RAG prompt                 │
│  2. Send to Ollama                   │
│  3. Receive answer                   │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  PIPELINE (app/pipeline.py)          │
│  1. Calculate response time          │
│  2. Log to PostgreSQL                │
│  3. Format response                  │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────┐
│ Return to    │
│    user      │
│              │
│ - Answer     │
│ - Sources    │
│ - Time       │
└──────────────┘
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                     │
│                                                             │
│  ┌──────────────────┐         ┌──────────────────┐        │
│  │   Streamlit      │         │   CLI (Python)   │        │
│  │   Web Interface  │         │   Command Line   │        │
│  └──────────────────┘         └──────────────────┘        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                       │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Python 3.8+                                         │  │
│  │                                                      │  │
│  │  - Query Pipeline                                    │  │
│  │  - Retrieval Logic                                   │  │
│  │  - Embeddings Manager                                │  │
│  │  - Document Ingestion                                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        AI/ML LAYER                          │
│                                                             │
│  ┌──────────────────┐         ┌──────────────────┐        │
│  │ Sentence         │         │  Ollama          │        │
│  │ Transformers     │         │  LLaMA-3         │        │
│  │                  │         │                  │        │
│  │ all-MiniLM-L6-v2 │         │  8B parameters   │        │
│  │ 384 dimensions   │         │  Local inference │        │
│  └──────────────────┘         └──────────────────┘        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                       STORAGE LAYER                         │
│                                                             │
│  ┌──────────────────┐         ┌──────────────────┐        │
│  │  FAISS           │         │  PostgreSQL      │        │
│  │  Vector Index    │         │  Relational DB   │        │
│  │                  │         │                  │        │
│  │  - IndexFlatIP   │         │  - Documents     │        │
│  │  - Cosine sim    │         │  - Chunks        │        │
│  │  - Disk persist  │         │  - Metadata      │        │
│  │                  │         │  - Query logs    │        │
│  └──────────────────┘         └──────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## File Dependencies

```
ui.py
  ├── pipeline.py
  │   ├── retrieval.py
  │   │   ├── embeddings.py
  │   │   ├── vector_store.py
  │   │   └── embeddings_manager.py
  │   │       └── database.py
  │   ├── llm.py
  │   └── database.py
  ├── ingestion.py
  │   └── database.py
  ├── embeddings_manager.py
  │   ├── embeddings.py
  │   ├── vector_store.py
  │   └── database.py
  └── config.py

All modules depend on:
  └── config.py (centralized configuration)
```

## Performance Characteristics

```
┌─────────────────────────────────────────────────────────────┐
│                    OPERATION TIMINGS                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Document Upload (1000 words)                              │
│  ├── Text extraction:        ~100ms                        │
│  ├── Chunking:               ~50ms                         │
│  ├── DB insert:              ~100ms                        │
│  └── Total:                  ~250ms                        │
│                                                             │
│  Embedding Generation (100 chunks)                         │
│  ├── Model load (first time): ~2s                          │
│  ├── Batch encoding:          ~1s                          │
│  ├── FAISS indexing:          ~50ms                        │
│  └── Total:                   ~1s (after warmup)           │
│                                                             │
│  Query Processing                                           │
│  ├── Question embedding:      ~50ms                        │
│  ├── FAISS search (10K vecs): ~10ms                        │
│  ├── DB fetch:                ~20ms                        │
│  ├── LLM inference:           ~2-5s                        │
│  └── Total:                   ~3-7s                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Scalability Profile

```
┌─────────────────────────────────────────────────────────────┐
│                    CURRENT CAPACITY                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Documents:        1,000s                                   │
│  Chunks:           100,000+                                 │
│  Vectors:          100,000+ (FAISS IndexFlatIP)            │
│  Concurrent Users: 1-5                                      │
│  Storage:          ~150KB per 1000 vectors                  │
│  Memory:           ~2GB (models + index)                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  SCALING STRATEGIES                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  For 1M+ vectors:                                           │
│  └── Use FAISS IVF index (approximate search)              │
│                                                             │
│  For more users:                                            │
│  └── Add Redis caching + load balancer                     │
│                                                             │
│  For faster inference:                                      │
│  └── Use GPU for embeddings + LLM                          │
│                                                             │
│  For better quality:                                        │
│  └── Add cross-encoder re-ranking                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```
