# app/embeddings.py
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL, EMBEDDING_DIM

print(f"[Embeddings] Loading model: {EMBEDDING_MODEL}")
_model = SentenceTransformer(EMBEDDING_MODEL)


def generate_embedding(text: str) -> np.ndarray:
    """Convert a single text string into an embedding vector."""
    embedding = _model.encode(text, convert_to_numpy=True)
    return embedding.astype(np.float32)


def generate_embeddings_batch(texts: list[str]) -> np.ndarray:
    """Convert a list of texts into embeddings all at once."""
    if not texts:
        return np.empty((0, EMBEDDING_DIM), dtype=np.float32)

    embeddings = _model.encode(
        texts,
        convert_to_numpy=True,
        batch_size=32,
        show_progress_bar=True
    )
    return embeddings.astype(np.float32)


def get_embedding_dimension() -> int:
    """Returns the size of the embedding vectors."""
    return EMBEDDING_DIM
