import hashlib
import json
import os
from typing import List, Tuple

import faiss
import numpy as np

from app.core.config import get_settings
from app.services.embedding_service import EmbeddingService
from app.services.pdf_service import chunk_text


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


class VectorService:
    def __init__(self):
        self.settings = get_settings()
        self.embedder = EmbeddingService()

    def _index_paths(self, doc_id: str) -> Tuple[str, str]:
        base = os.path.join(self.settings.faiss_index_dir, doc_id)
        return base + ".index", base + ".meta.json"

    def build_index(self, pdf_bytes: bytes) -> Tuple[str, faiss.Index, List[str]]:
        doc_text = self._load_and_chunk(pdf_bytes)
        chunks = doc_text
        vectors = self.embedder.embed_texts(chunks)
        vectors = np.asarray(vectors).astype("float32")

        dim = vectors.shape[1]
        index = faiss.IndexFlatIP(dim)  # cosine via normalized embeddings (IP)
        index.add(vectors)
        return _sha256_bytes(pdf_bytes), index, chunks

    def _load_and_chunk(self, pdf_bytes: bytes) -> List[str]:
        from app.services.pdf_service import extract_pdf_text

        raw = extract_pdf_text(pdf_bytes)
        return chunk_text(raw)

    def save_index(self, doc_id: str, index: faiss.Index, chunks: List[str]):
        os.makedirs(self.settings.faiss_index_dir, exist_ok=True)
        index_path, meta_path = self._index_paths(doc_id)
        faiss.write_index(index, index_path)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump({"chunks": chunks}, f, ensure_ascii=False)

    def load_index(self, doc_id: str) -> Tuple[faiss.Index, List[str]]:
        index_path, meta_path = self._index_paths(doc_id)
        index = faiss.read_index(index_path)
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        return index, meta["chunks"]

    def build_or_load(self, pdf_bytes: bytes) -> Tuple[str, faiss.Index, List[str]]:
        doc_id = _sha256_bytes(pdf_bytes)
        index_path, meta_path = self._index_paths(doc_id)

        if os.path.exists(index_path) and os.path.exists(meta_path):
            index, chunks = self.load_index(doc_id)
            return doc_id, index, chunks

        _, index, chunks = self.build_index(pdf_bytes)
        self.save_index(doc_id, index, chunks)
        return doc_id, index, chunks

    def build_or_load_text(self, text: str, doc_id_seed: str) -> Tuple[str, faiss.Index, List[str]]:
        doc_id = hashlib.sha256(doc_id_seed.encode("utf-8")).hexdigest()
        index_path, meta_path = self._index_paths(doc_id)

        if os.path.exists(index_path) and os.path.exists(meta_path):
            index, chunks = self.load_index(doc_id)
            return doc_id, index, chunks

        chunks = chunk_text(text)
        vectors = self.embedder.embed_texts(chunks)
        vectors = np.asarray(vectors).astype("float32")

        dim = vectors.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(vectors)
        self.save_index(doc_id, index, chunks)
        return doc_id, index, chunks

    def query(self, question: str, index: faiss.Index, chunks: List[str], top_k: int = 5) -> List[str]:
        q_vec = self.embedder.embed_texts([question])
        q_vec = np.asarray(q_vec).astype("float32")
        scores, idxs = index.search(q_vec, top_k)
        # Return chunks by retrieved indices
        res: List[str] = []
        for i in idxs[0].tolist():
            if 0 <= i < len(chunks):
                res.append(chunks[i])
        return res


vector_service_singleton = VectorService()


def build_or_load_index_for_upload(pdf_bytes: bytes) -> Tuple[str, faiss.Index, List[str]]:
    return vector_service_singleton.build_or_load(pdf_bytes)


def build_or_load_index_for_text(text: str, doc_id_seed: str) -> Tuple[str, faiss.Index, List[str]]:
    return vector_service_singleton.build_or_load_text(text, doc_id_seed)

