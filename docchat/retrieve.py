"""Retrieval functions that turn Chroma results into source chunks."""

from __future__ import annotations

from dataclasses import dataclass

from docchat.embeddings import embed_texts
from docchat.store import DocumentStore


@dataclass(frozen=True)
class RetrievedChunk:
    text: str
    file_name: str
    page_number: int
    distance: float


def retrieve(question: str, store: DocumentStore, limit: int = 4) -> list[RetrievedChunk]:
    """Find the nearest chunks for a non-empty question."""
    if not question.strip() or store.count() == 0:
        return []
    result = store.query(embed_texts([question])[0], limit)
    documents = result["documents"][0]
    metadata = result["metadatas"][0]
    distances = result["distances"][0]
    return [
        RetrievedChunk(
            text=document,
            file_name=item["file_name"],
            page_number=int(item["page_number"]),
            distance=float(distance),
        )
        for document, item, distance in zip(documents, metadata, distances)
    ]
