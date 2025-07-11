from typing import List, Any
import faiss
import numpy as np


class VectorStore:
    """FAISS-based vector store."""

    def __init__(self):
        self.index = None
        self.meta: List[Any] = []

    def build(self, embeddings: np.ndarray, metadata: List[Any]):
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings.astype('float32'))
        self.meta = metadata

    def search(self, vector: np.ndarray, k: int = 3):
        if self.index is None:
            raise ValueError("Index not built")
        distances, idx = self.index.search(vector.astype('float32'), k)
        results = [self.meta[i] for i in idx[0]]
        return results, distances[0]
