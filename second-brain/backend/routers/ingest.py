from fastapi import APIRouter, File, HTTPException, UploadFile

from core.embedder import ingest_file

router = APIRouter(tags=["ingest"])


@router.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    try:
        content = await file.read()
        result = ingest_file(content, file.filename or "uploaded_file")
        return {
            "success": True,
            "filename": file.filename,
            **result,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
