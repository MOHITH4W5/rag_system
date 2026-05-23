from fastapi import APIRouter, HTTPException

from app.database import get_db_connection
from app.vector_store import FAISSVectorStore

router = APIRouter(tags=["documents"])


def _resolve_uploaded_column(cursor) -> str:
    cursor.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'documents'
          AND column_name IN ('uploaded_at', 'upload_date')
        ORDER BY CASE column_name WHEN 'uploaded_at' THEN 0 ELSE 1 END
        LIMIT 1
        """
    )
    row = cursor.fetchone()
    return row[0] if row else "upload_date"


@router.get("/documents")
def list_documents():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                uploaded_col = _resolve_uploaded_column(cursor)
                cursor.execute(
                    f"""
                    SELECT d.id, d.filename, d.file_type, d.{uploaded_col}, COUNT(dc.id) AS chunk_count
                    FROM documents d
                    LEFT JOIN document_chunks dc ON dc.document_id = d.id
                    GROUP BY d.id, d.filename, d.file_type, d.{uploaded_col}
                    ORDER BY d.{uploaded_col} DESC
                    """
                )
                rows = cursor.fetchall()

        return [
            {
                "id": row[0],
                "filename": row[1],
                "file_type": row[2],
                "uploaded_at": str(row[3]),
                "chunk_count": row[4],
            }
            for row in rows
        ]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: int):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM document_chunks WHERE document_id = %s", (doc_id,))
                chunk_ids = [row[0] for row in cursor.fetchall()]

                if chunk_ids:
                    store = FAISSVectorStore()
                    store.delete_by_chunk_ids(chunk_ids)

                cursor.execute("DELETE FROM documents WHERE id = %s", (doc_id,))
            conn.commit()

        return {"success": True}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
