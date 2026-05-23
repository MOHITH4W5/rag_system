# app/vector_store.py
import os
import json
import numpy as np
import faiss
from app.config import FAISS_INDEX_PATH, FAISS_ID_MAP_PATH, EMBEDDING_DIM

os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)


class FAISSVectorStore:
    """Manages a FAISS index for vector similarity search."""

    def __init__(self):
        self.dimension = EMBEDDING_DIM
        self.index = None
        self.id_map = {}
        self._load_or_create()

    def _load_or_create(self):
        """Load existing index from disk, or create a fresh one."""
        if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(FAISS_ID_MAP_PATH):
            print("[FAISS] Loading existing index from disk...")
            self.index = faiss.read_index(FAISS_INDEX_PATH)
            with open(FAISS_ID_MAP_PATH, "r") as f:
                self.id_map = {int(k): v for k, v in json.load(f).items()}
            print(f"[FAISS] Loaded {self.index.ntotal} vectors")
        else:
            print("[FAISS] Creating new index...")
            self.index = faiss.IndexFlatIP(self.dimension)
            self.id_map = {}

    def add_embeddings(self, embeddings: np.ndarray, chunk_ids: list):
        """Add a batch of embeddings to the index."""
        if len(embeddings) == 0:
            return

        faiss.normalize_L2(embeddings)
        start_id = self.index.ntotal

        self.index.add(embeddings)

        for i, chunk_id in enumerate(chunk_ids):
            self.id_map[start_id + i] = chunk_id

        self.save()
        print(f"[FAISS] Added {len(embeddings)} vectors. Total: {self.index.ntotal}")

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> list[dict]:
        """Find the top_k most similar chunks for a query embedding."""
        if self.index.ntotal == 0:
            print("[FAISS] Index is empty. No results.")
            return []

        query = query_embedding.reshape(1, -1).astype(np.float32)
        faiss.normalize_L2(query)

        scores, indices = self.index.search(query, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            chunk_id = self.id_map.get(idx)
            if chunk_id is not None:
                results.append({
                    "chunk_id": chunk_id,
                    "score": float(score)
                })

        return results

    def save(self):
        """Persist the index and ID map to disk."""
        faiss.write_index(self.index, FAISS_INDEX_PATH)
        with open(FAISS_ID_MAP_PATH, "w") as f:
            json.dump(self.id_map, f)

    def get_total_vectors(self) -> int:
        return self.index.ntotal if self.index else 0

    def delete_by_chunk_ids(self, chunk_ids: list):
        """Remove specific vectors by rebuilding the index."""
        if not chunk_ids:
            return

        chunk_id_set = set(chunk_ids)
        surviving_faiss_ids = [
            fid for fid, cid in self.id_map.items()
            if cid not in chunk_id_set
        ]

        if not surviving_faiss_ids:
            self.index = faiss.IndexFlatIP(self.dimension)
            self.id_map = {}
            self.save()
            return

        all_vectors = self.index.reconstruct_n(0, self.index.ntotal)
        surviving_vectors = np.array([all_vectors[i] for i in surviving_faiss_ids])
        surviving_chunk_ids = [self.id_map[i] for i in surviving_faiss_ids]

        self.index = faiss.IndexFlatIP(self.dimension)
        self.id_map = {}
        self.add_embeddings(surviving_vectors, surviving_chunk_ids)
        print(f"[FAISS] Rebuilt index. Remaining vectors: {self.index.ntotal}")
