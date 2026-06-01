from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db_connection
from core.security import create_access_token, get_current_user, verify_password
from schemas.models import LoginRequest

router = APIRouter(tags=["auth"])


@router.post("/auth/login")
def login(payload: LoginRequest):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, username, password_hash, role
                FROM users
                WHERE username = %s
                """,
                (payload.username.strip(),),
            )
            row = cursor.fetchone()

    if not row or not verify_password(payload.password, row[2]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    token = create_access_token(user_id=row[0], username=row[1], role=row[3])
    return {"access_token": token, "token_type": "bearer"}


@router.get("/auth/me")
def me(current_user: dict = Depends(get_current_user)):
    return {"id": current_user["id"], "username": current_user["username"], "role": current_user["role"]}
