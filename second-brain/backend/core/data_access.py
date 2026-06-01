from app.database import get_db_connection


def get_accessible_document_ids(user_id: int, role: str) -> set[int]:
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            if role == "admin":
                cursor.execute("SELECT id FROM documents")
            else:
                cursor.execute(
                    """
                    SELECT id
                    FROM documents
                    WHERE visibility_scope = 'global'
                       OR (visibility_scope = 'private' AND owner_user_id = %s)
                    """,
                    (user_id,),
                )
            rows = cursor.fetchall()
    return {row[0] for row in rows}


def get_document_owner_and_scope(doc_id: int):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT d.owner_user_id, d.visibility_scope
                FROM documents d
                WHERE d.id = %s
                """,
                (doc_id,),
            )
            return cursor.fetchone()


def log_user_query(user_id: int, question: str, answer: str, retrieved_chunk_ids: list[int], response_time_ms: int):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO query_logs
                    (user_id, question, answer, retrieved_chunk_ids, response_time_ms, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
                """,
                (user_id, question, answer, retrieved_chunk_ids, response_time_ms),
            )
        conn.commit()
