import PyPDF2
from docx import Document

from app.database import get_db_connection


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
    return text


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a DOCX file."""
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])


def extract_text_from_txt(file_path: str) -> str:
    """Extract text from a TXT file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0:
        raise ValueError("overlap must be >= 0")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    words = text.split()
    chunks = []
    step = chunk_size - overlap

    for i in range(0, len(words), step):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)

    return chunks


def ingest_document(file_path: str, filename: str) -> int:
    """
    Ingest a document: extract text, chunk it, save to database.
    Returns the document_id.
    """
    print(f"[Ingestion] Processing {filename}...")

    if filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
        file_type = "pdf"
    elif filename.lower().endswith(".docx"):
        text = extract_text_from_docx(file_path)
        file_type = "docx"
    elif filename.lower().endswith(".txt"):
        text = extract_text_from_txt(file_path)
        file_type = "txt"
    else:
        raise ValueError(f"Unsupported file type: {filename}")

    chunks = chunk_text(text)

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO documents (filename, file_type, file_size)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (filename, file_type, len(text)),
            )
            document_id = cursor.fetchone()[0]

            for idx, chunk in enumerate(chunks):
                cursor.execute(
                    """
                    INSERT INTO document_chunks (document_id, chunk_text, chunk_index, token_count)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (document_id, chunk, idx, len(chunk.split())),
                )

        conn.commit()

    print(f"[Ingestion] Saved {len(chunks)} chunks for document {document_id}")
    return document_id