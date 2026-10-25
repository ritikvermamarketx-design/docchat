"""Run retrieval and evidence-keyword checks against the bundled PDFs."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from docchat.embeddings import embed_texts
from docchat.ingest import chunk_pages, file_fingerprint, read_pdf
from docchat.retrieve import retrieve
from docchat.store import DocumentStore

ROOT = Path(__file__).resolve().parents[1]
EVAL_STORE = ROOT / ".eval_chroma"


def build_store() -> DocumentStore:
    """Create a fresh local index from the two sample PDFs."""
    if EVAL_STORE.exists():
        shutil.rmtree(EVAL_STORE)
    store = DocumentStore(EVAL_STORE)
    for pdf in sorted((ROOT / "sample_docs").glob("*.pdf")):
        data = pdf.read_bytes()
        chunks = chunk_pages(read_pdf(pdf.name, data))
        store.add_chunks(chunks, embed_texts([chunk.text for chunk in chunks]), file_fingerprint(data))
    return store


def main() -> None:
    cases = json.loads((ROOT / "evals" / "questions.json").read_text())
    store = build_store()
    hits = 0
    checks = 0
    rows: list[str] = []
    for case in cases:
        sources = retrieve(case["question"], store, limit=4)
        hit = any(source.file_name == case["file"] and source.page_number == case["page"] for source in sources)
        evidence = " ".join(source.text.lower() for source in sources)
        keyword_check = all(keyword.lower() in evidence for keyword in case["keywords"])
        hits += hit
        checks += keyword_check
        rows.append(f"| {case['question']} | {'yes' if hit else 'no'} | {'yes' if keyword_check else 'no'} |")

    total = len(cases)
    report = [
        "# Evaluation results",
        "",
        f"Run locally against the bundled PDFs with `python evals/run_evals.py`.",
        "",
        f"- Retrieval hit rate at top-4: **{hits}/{total} ({hits / total:.0%})**",
        f"- Evidence keyword check: **{checks}/{total} ({checks / total:.0%})**",
        "",
        "The answer check is offline: it verifies that all expected answer keywords appear in the retrieved evidence. It is a groundedness proxy, not an LLM judge.",
        "",
        "| Question | Expected page in top-4 | Evidence keywords found |",
        "| --- | --- | --- |",
        *rows,
        "",
        "This is the baseline for the current 700-character chunks with 120-character overlap. Future changes should be compared against these two figures.",
    ]
    (ROOT / "evals" / "results.md").write_text("\n".join(report) + "\n")
    print(f"retrieval hit rate: {hits}/{total} ({hits / total:.0%})")
    print(f"evidence keyword check: {checks}/{total} ({checks / total:.0%})")


if __name__ == "__main__":
    main()
