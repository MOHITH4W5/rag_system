import tempfile
from pathlib import Path
import os


def ingest_file(raw_bytes: bytes, filename: str, owner_user_id: int, visibility_scope: str):
    from app.embeddings_manager import embed_document
    from app.ingestion import ingest_document

    suffix = Path(filename).suffix
    tmp_path = None
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(raw_bytes)
        tmp_path = tmp.name

    try:
        doc_id = ingest_document(
            tmp_path,
            filename,
            owner_user_id=owner_user_id,
            visibility_scope=visibility_scope,
        )
        chunks = embed_document(doc_id)
        return {"document_id": doc_id, "chunks_processed": chunks}
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
