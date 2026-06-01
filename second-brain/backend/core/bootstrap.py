import os

from app.database import get_db_connection

from core.security import hash_password


def _column_exists(cursor, table: str, column: str) -> bool:
    cursor.execute(
        """
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = %s AND column_name = %s
        LIMIT 1
        """,
        (table, column),
    )
    return cursor.fetchone() is not None


def ensure_multitenant_schema():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'user')),
                    created_at TIMESTAMP DEFAULT NOW()
                )
                """
            )

            cursor.execute(
                """
                ALTER TABLE documents
                ADD COLUMN IF NOT EXISTS visibility_scope VARCHAR(20) DEFAULT 'private'
                """
            )
            cursor.execute(
                """
                ALTER TABLE documents
                ADD COLUMN IF NOT EXISTS owner_user_id INTEGER REFERENCES users(id)
                """
            )
            cursor.execute(
                """
                ALTER TABLE query_logs
                ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id)
                """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_documents_owner_user_id
                ON documents(owner_user_id)
                """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_documents_visibility_scope
                ON documents(visibility_scope)
                """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_query_logs_user_id
                ON query_logs(user_id)
                """
            )

        conn.commit()


def seed_demo_users():
    admin_password = os.getenv("SEED_ADMIN_PASSWORD", "admin123")
    user1_password = os.getenv("SEED_USER1_PASSWORD", "user123")
    user2_password = os.getenv("SEED_USER2_PASSWORD", "user123")

    seeds = [
        ("admin", admin_password, "admin"),
        ("user1", user1_password, "user"),
        ("user2", user2_password, "user"),
    ]

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            for username, raw_password, role in seeds:
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                row = cursor.fetchone()
                if row:
                    continue
                cursor.execute(
                    """
                    INSERT INTO users (username, password_hash, role)
                    VALUES (%s, %s, %s)
                    """,
                    (username, hash_password(raw_password), role),
                )
        conn.commit()


def backfill_existing_documents_to_admin_global():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE role = 'admin' ORDER BY id ASC LIMIT 1")
            admin_row = cursor.fetchone()
            if not admin_row:
                return
            admin_id = admin_row[0]

            has_uploaded_at = _column_exists(cursor, "documents", "uploaded_at")
            has_upload_date = _column_exists(cursor, "documents", "upload_date")
            timestamp_col = "uploaded_at" if has_uploaded_at else "upload_date" if has_upload_date else None

            if timestamp_col:
                cursor.execute(
                    f"""
                    UPDATE documents
                    SET owner_user_id = %s,
                        visibility_scope = 'global'
                    WHERE owner_user_id IS NULL
                       OR visibility_scope IS NULL
                    """,
                    (admin_id,),
                )
            else:
                cursor.execute(
                    """
                    UPDATE documents
                    SET owner_user_id = %s,
                        visibility_scope = 'global'
                    WHERE owner_user_id IS NULL
                       OR visibility_scope IS NULL
                    """,
                    (admin_id,),
                )
        conn.commit()
