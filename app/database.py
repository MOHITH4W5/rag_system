from pathlib import Path

import psycopg2

from app.config import DATABASE_URL


def get_db_connection():
    """Create a new PostgreSQL connection."""
    return psycopg2.connect(DATABASE_URL)


def get_connection():
    """Backward-compatible alias used by older modules."""
    return get_db_connection()


def test_connection() -> bool:
    """Test if database connection works."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
        print(f"[DB] Connected: {version[0]}")
        return True
    except Exception as exc:
        print(f"[DB] Connection failed: {exc}")
        return False


def _resolve_schema_path(schema_path: str | None = None) -> Path:
    if schema_path:
        return Path(schema_path).resolve()
    return (Path(__file__).resolve().parent.parent / "schema.sql").resolve()


def init_db(schema_path: str | None = None):
    """
    Initialize DB tables/indexes from schema.sql.
    Safe to call repeatedly when schema uses IF NOT EXISTS.
    """
    path = _resolve_schema_path(schema_path)
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found at: {path}")

    schema_sql = path.read_text(encoding="utf-8")
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(schema_sql)
        conn.commit()


def get_all_documents():
    """Get list of all documents."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, filename, file_type, upload_date
                FROM documents
                ORDER BY upload_date DESC
                """
            )
            rows = cursor.fetchall()
    return rows


def get_document_stats(document_id: int):
    """Get statistics for a document."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*) FROM document_chunks WHERE document_id = %s
                """,
                (document_id,),
            )
            chunk_count = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM embeddings_metadata em
                JOIN document_chunks dc ON dc.id = em.chunk_id
                WHERE dc.document_id = %s
                """,
                (document_id,),
            )
            embedded_count = cursor.fetchone()[0]
    return {"chunks": chunk_count, "embedded": embedded_count}
