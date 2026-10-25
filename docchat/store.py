"""Small persistence wrapper around ChromaDB."""

from __future__ import annotations

from pathlib import Path

import chromadb
from chromadb.config import Settings

from docchat.ingest import TextChunk


class DocumentStore:
    """Persist and query document chunks using precomputed embeddings."""

    def __init__(self, directory: str | Path = "chroma_data") -> None:
        self.client = chromadb.PersistentClient(
            path=str(directory), settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name="docchat_chunks", metadata={"hnsw:space": "cosine"}
        )

    def has_fingerprint(self, fingerprint: str) -> bool:
        return bool(self.collection.get(where={"fingerprint": fingerprint}, limit=1)["ids"])

    def add_chunks(self, chunks: list[TextChunk], embeddings: list[list[float]], fingerprint: str) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings must have equal length")
        self.collection.upsert(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            embeddings=embeddings,
            metadatas=[
                {"file_name": chunk.file_name, "page_number": chunk.page_number, "fingerprint": fingerprint}
                for chunk in chunks
            ],
        )

    def query(self, embedding: list[float], limit: int) -> dict[str, list]:
        return self.collection.query(query_embeddings=[embedding], n_results=limit)

    def count(self) -> int:
        return self.collection.count()
