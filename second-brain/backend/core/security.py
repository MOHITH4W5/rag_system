import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.database import get_db_connection

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)

JWT_SECRET = os.getenv("JWT_SECRET", "change_this_for_production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "720"))


def hash_password(raw_password: str) -> str:
    return pwd_context.hash(raw_password)


def verify_password(raw_password: str, password_hash: str) -> bool:
    return pwd_context.verify(raw_password, password_hash)


def create_access_token(user_id: int, username: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=JWT_EXPIRE_MINUTES)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> dict:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token",
        )

    payload = _decode_token(credentials.credentials)
    user_id = int(payload.get("sub", "0"))
    if user_id <= 0:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, username, role
                FROM users
                WHERE id = %s
                """,
                (user_id,),
            )
            row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists")

    return {"id": row[0], "username": row[1], "role": row[2]}


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user
