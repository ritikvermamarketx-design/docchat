"""PDF parsing and page-aware text chunking."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from typing import BinaryIO

from pypdf import PdfReader


@dataclass(frozen=True)
class PageText:
    file_name: str
    page_number: int
    text: str


@dataclass(frozen=True)
class TextChunk:
    chunk_id: str
    file_name: str
    page_number: int
    text: str


def read_pdf(file_name: str, source: BinaryIO | bytes) -> list[PageText]:
    """Extract non-empty text from each page of a PDF."""
    stream = BytesIO(source) if isinstance(source, bytes) else source
    reader = PdfReader(stream)
    pages: list[PageText] = []
    for number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append(PageText(file_name=file_name, page_number=number, text=text))
    return pages


def chunk_pages(pages: list[PageText], chunk_size: int = 700, overlap: int = 120) -> list[TextChunk]:
    """Split pages into overlapping character chunks without crossing page boundaries."""
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_size must be positive and overlap must be smaller than it")

    chunks: list[TextChunk] = []
    for page in pages:
        start = 0
        chunk_index = 0
        while start < len(page.text):
            end = min(start + chunk_size, len(page.text))
            if end < len(page.text):
                boundary = page.text.rfind(" ", start + chunk_size // 2, end)
                if boundary > start:
                    end = boundary
            text = page.text[start:end].strip()
            if text:
                digest = sha256(f"{page.file_name}:{page.page_number}:{chunk_index}:{text}".encode()).hexdigest()
                chunks.append(TextChunk(digest, page.file_name, page.page_number, text))
                chunk_index += 1
            if end >= len(page.text):
                break
            start = max(end - overlap, start + 1)
    return chunks


def file_fingerprint(data: bytes) -> str:
    """Return a stable content hash for duplicate-upload detection."""
    return sha256(data).hexdigest()


def safe_file_name(name: str) -> str:
    """Strip path components from browser-provided names."""
    return Path(name).name
