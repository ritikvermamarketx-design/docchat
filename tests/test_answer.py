from docchat.answer import NOT_FOUND_MESSAGE, answer_question, format_citation
from docchat.retrieve import RetrievedChunk


class FakeLLM:
    def __init__(self, answer: str) -> None:
        self.answer = answer

    def complete(self, prompt: str) -> str:
        return self.answer


def test_format_citation() -> None:
    assert format_citation("notes.pdf", 12) == "notes.pdf, p. 12"


def test_not_found_when_no_sources() -> None:
    assert answer_question("What is the policy?", [], FakeLLM("anything")) == NOT_FOUND_MESSAGE


def test_not_found_when_model_returns_sentinel() -> None:
    sources = [RetrievedChunk("Policy text", "guide.pdf", 1, 0.1)]
    assert answer_question("What is the policy?", sources, FakeLLM("NOT_FOUND")) == NOT_FOUND_MESSAGE
