from app.config import EMBEDDING_MODEL
from app.database import get_db_connection
from app.embeddings import generate_embeddings_batch
from app.vector_store import FAISSVectorStore


def get_unembedded_chunks(document_id: int | None = None) -> list[dict]:
    """Fetch chunks from DB that have not been embedded yet."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            if document_id:
                cursor.execute(
                    """
                    SELECT dc.id, dc.chunk_text, dc.chunk_index, dc.document_id
                    FROM document_chunks dc
                    LEFT JOIN embeddings_metadata em ON em.chunk_id = dc.id
                    WHERE dc.document_id = %s AND em.chunk_id IS NULL
                    ORDER BY dc.chunk_index
                    """,
                    (document_id,),
                )
            else:
                cursor.execute(
                    """
                    SELECT dc.id, dc.chunk_text, dc.chunk_index, dc.document_id
                    FROM document_chunks dc
                    LEFT JOIN embeddings_metadata em ON em.chunk_id = dc.id
                    WHERE em.chunk_id IS NULL
                    ORDER BY dc.document_id, dc.chunk_index
                    """
                )
            rows = cursor.fetchall()

    return [
        {"id": r[0], "chunk_text": r[1], "chunk_index": r[2], "document_id": r[3]}
        for r in rows
    ]


def mark_chunks_as_embedded(chunk_ids: list[int], model_name: str):
    """Record in DB that these chunks now have embeddings in FAISS."""
    if not chunk_ids:
        return

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            for chunk_id in chunk_ids:
                cursor.execute(
                    """
                    INSERT INTO embeddings_metadata (chunk_id, model_name, created_at)
                    VALUES (%s, %s, NOW())
                    ON CONFLICT (chunk_id) DO NOTHING
                    """,
                    (chunk_id, model_name),
                )
        conn.commit()


def embed_document(document_id: int) -> int:
    """Embed all not-yet-embedded chunks for one document."""
    print(f"[EmbedManager] Embedding document {document_id}...")

    chunks = get_unembedded_chunks(document_id)
    if not chunks:
        print("[EmbedManager] All chunks already embedded.")
        return 0

    texts = [c["chunk_text"] for c in chunks]
    chunk_ids = [c["id"] for c in chunks]

    embeddings = generate_embeddings_batch(texts)

    store = FAISSVectorStore()
    store.add_embeddings(embeddings, chunk_ids)

    mark_chunks_as_embedded(chunk_ids, EMBEDDING_MODEL)

    print(f"[EmbedManager] Embedded {len(chunks)} chunks for document {document_id}")
    return len(chunks)


def get_chunks_by_ids(chunk_ids: list[int]) -> list[dict]:
    """Retrieve full chunk rows by chunk IDs."""
    if not chunk_ids:
        return []

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            placeholders = ",".join(["%s"] * len(chunk_ids))
            cursor.execute(
                f"""
                SELECT
                    dc.id,
                    dc.chunk_text,
                    dc.chunk_index,
                    dc.document_id,
                    d.filename,
                    d.title
                FROM document_chunks dc
                JOIN documents d ON d.id = dc.document_id
                WHERE dc.id IN ({placeholders})
                """,
                chunk_ids,
            )
            rows = cursor.fetchall()

    by_id = {
        r[0]: {
            "chunk_id": r[0],
            "chunk_text": r[1],
            "chunk_index": r[2],
            "document_id": r[3],
            "filename": r[4],
            "title": r[5],
        }
        for r in rows
    }

    # Preserve incoming FAISS order.
    return [by_id[cid] for cid in chunk_ids if cid in by_id]