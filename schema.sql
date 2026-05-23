-- PostgreSQL Schema for RAG Document Management System

CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    file_type VARCHAR(50),
    file_size INTEGER,
    upload_date TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    token_count INTEGER
);

CREATE TABLE IF NOT EXISTS embeddings_metadata (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER UNIQUE REFERENCES document_chunks(id) ON DELETE CASCADE,
    model_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS query_logs (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT,
    retrieved_chunk_ids INTEGER[],
    response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id
    ON document_chunks(document_id);

CREATE INDEX IF NOT EXISTS idx_embeddings_metadata_chunk_id
    ON embeddings_metadata(chunk_id);

CREATE INDEX IF NOT EXISTS idx_query_logs_created_at
    ON query_logs(created_at);