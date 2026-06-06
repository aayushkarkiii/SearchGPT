from typing import List

from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = SentenceTransformer(model_name)

    def embed_texts(self, texts: List[str]):
        # Returns np.ndarray [n, dim]
        return self._model.encode(texts, normalize_embeddings=True)

