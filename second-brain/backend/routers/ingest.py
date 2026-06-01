from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from core.embedder import ingest_file
from core.security import get_current_user

router = APIRouter(tags=["ingest"])


@router.post("/ingest")
async def ingest(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    try:
        content = await file.read()
        visibility_scope = "global" if current_user["role"] == "admin" else "private"
        result = ingest_file(
            content,
            file.filename or "uploaded_file",
            owner_user_id=current_user["id"],
            visibility_scope=visibility_scope,
        )
        return {
            "success": True,
            "filename": file.filename,
            "visibility_scope": visibility_scope,
            **result,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
