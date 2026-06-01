from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db_connection
from app.vector_store import FAISSVectorStore
from core.data_access import get_document_owner_and_scope
from core.security import get_current_user

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
def list_documents(current_user: dict = Depends(get_current_user)):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                uploaded_col = _resolve_uploaded_column(cursor)
                if current_user["role"] == "admin":
                    cursor.execute(
                        f"""
                        SELECT d.id, d.filename, d.file_type, d.{uploaded_col}, d.visibility_scope, d.owner_user_id,
                               COALESCE(u.username, 'unknown') AS owner_username, COUNT(dc.id) AS chunk_count
                        FROM documents d
                        LEFT JOIN users u ON u.id = d.owner_user_id
                        LEFT JOIN document_chunks dc ON dc.document_id = d.id
                        GROUP BY d.id, d.filename, d.file_type, d.{uploaded_col}, d.visibility_scope, d.owner_user_id, u.username
                        ORDER BY d.{uploaded_col} DESC
                        """
                    )
                else:
                    cursor.execute(
                        f"""
                        SELECT d.id, d.filename, d.file_type, d.{uploaded_col}, d.visibility_scope, d.owner_user_id,
                               COALESCE(u.username, 'unknown') AS owner_username, COUNT(dc.id) AS chunk_count
                        FROM documents d
                        LEFT JOIN users u ON u.id = d.owner_user_id
                        LEFT JOIN document_chunks dc ON dc.document_id = d.id
                        WHERE d.visibility_scope = 'global'
                           OR (d.visibility_scope = 'private' AND d.owner_user_id = %s)
                        GROUP BY d.id, d.filename, d.file_type, d.{uploaded_col}, d.visibility_scope, d.owner_user_id, u.username
                        ORDER BY d.{uploaded_col} DESC
                        """,
                        (current_user["id"],),
                    )
                rows = cursor.fetchall()

        return [
            {
                "id": row[0],
                "filename": row[1],
                "file_type": row[2],
                "uploaded_at": str(row[3]),
                "visibility_scope": row[4],
                "owner_user_id": row[5],
                "owner_username": row[6],
                "is_global": row[4] == "global",
                "chunk_count": row[7],
            }
            for row in rows
        ]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: int, current_user: dict = Depends(get_current_user)):
    try:
        doc_meta = get_document_owner_and_scope(doc_id)
        if not doc_meta:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        owner_user_id, visibility_scope = doc_meta
        if current_user["role"] != "admin":
            if visibility_scope == "global" or owner_user_id != current_user["id"]:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to delete this document")

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
