from docchat.ingest import PageText, chunk_pages


def test_chunking_keeps_page_numbers_and_overlap() -> None:
    pages = [PageText("guide.pdf", 3, "alpha beta gamma delta epsilon zeta eta theta")]
    chunks = chunk_pages(pages, chunk_size=18, overlap=6)

    assert len(chunks) >= 3
    assert all(chunk.file_name == "guide.pdf" and chunk.page_number == 3 for chunk in chunks)
    assert "beta" in chunks[0].text and "beta" in chunks[1].text
    assert chunks[-1].text.endswith("theta")


def test_chunking_rejects_invalid_overlap() -> None:
    page = PageText("guide.pdf", 1, "short text")
    try:
        chunk_pages([page], chunk_size=20, overlap=20)
    except ValueError:
        return
    raise AssertionError("Expected invalid overlap to raise ValueError")
