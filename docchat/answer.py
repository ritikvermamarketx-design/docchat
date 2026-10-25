"""Grounded-answer prompting and presentation helpers."""

from __future__ import annotations

from docchat.llm import LLMClient
from docchat.retrieve import RetrievedChunk

NOT_FOUND_MESSAGE = "I could not find that in the uploaded documents."


def format_citation(file_name: str, page_number: int) -> str:
    """Format a source label used in answers and the UI."""
    return f"{file_name}, p. {page_number}"


def build_prompt(question: str, sources: list[RetrievedChunk]) -> str:
    """Build a bounded prompt containing only retrieved document text."""
    context = "\n\n".join(
        f"SOURCE [{format_citation(source.file_name, source.page_number)}]\n{source.text}"
        for source in sources
    )
    return f"""Answer the question using only the source text below.
If the source text does not answer it, reply with exactly NOT_FOUND.
Do not add outside facts. Use concise prose and cite each factual sentence with its
source label in square brackets, for example [handbook.pdf, p. 2].

Question: {question}

Source text:
{context}"""


def answer_question(question: str, sources: list[RetrievedChunk], llm: LLMClient) -> str:
    """Generate a grounded answer, returning a safe response when evidence is absent."""
    if not sources:
        return NOT_FOUND_MESSAGE
    answer = llm.complete(build_prompt(question, sources)).strip()
    if not answer or answer.upper() == "NOT_FOUND":
        return NOT_FOUND_MESSAGE
    return answer
