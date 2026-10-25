"""Streamlit entry point for DocChat."""

from __future__ import annotations

import logging

import streamlit as st
from dotenv import load_dotenv
from pypdf.errors import PdfReadError

from docchat.answer import answer_question
from docchat.embeddings import embed_texts
from docchat.ingest import chunk_pages, file_fingerprint, read_pdf, safe_file_name
from docchat.llm import LLMConfigurationError, get_llm
from docchat.retrieve import retrieve
from docchat.store import DocumentStore

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)
MAX_FILE_BYTES = 25 * 1024 * 1024

load_dotenv()
st.set_page_config(page_title="DocChat", page_icon="D", layout="wide")


@st.cache_resource
def get_store() -> DocumentStore:
    return DocumentStore()


def index_uploads() -> None:
    """Validate uploaded PDFs and add their chunks to the local store."""
    uploads = st.session_state.get("uploads", [])
    store = get_store()
    for upload in uploads:
        data = upload.getvalue()
        name = safe_file_name(upload.name)
        if len(data) > MAX_FILE_BYTES:
            st.warning(f"{name} is larger than the 25 MB limit and was skipped.")
            continue
        fingerprint = file_fingerprint(data)
        if store.has_fingerprint(fingerprint):
            st.info(f"{name} was already indexed, so it was skipped.")
            continue
        try:
            pages = read_pdf(name, data)
        except (PdfReadError, ValueError, OSError) as error:
            logger.info("Could not read %s: %s", name, error)
            st.warning(f"{name} could not be read as a PDF and was skipped.")
            continue
        if not pages:
            st.warning(f"{name} has no extractable text. It may be a scanned PDF.")
            continue
        chunks = chunk_pages(pages)
        with st.spinner(f"Indexing {name} ({len(chunks)} chunks)..."):
            store.add_chunks(chunks, embed_texts([chunk.text for chunk in chunks]), fingerprint)
        st.success(f"Indexed {name}: {len(pages)} text pages, {len(chunks)} chunks.")


st.title("DocChat")
st.caption("Upload PDFs, then ask questions with page-level citations.")

with st.sidebar:
    st.header("Documents")
    st.file_uploader(
        "Upload PDF files", type=["pdf"], accept_multiple_files=True, key="uploads",
        help="Files are stored only in the local Chroma index. Maximum size: 25 MB each.",
    )
    if st.button("Index uploaded PDFs", type="primary", use_container_width=True):
        index_uploads()
    st.caption(f"{get_store().count()} indexed chunks in the local store")
    st.divider()
    st.caption("Try the included PDFs in sample_docs/ for a local demo.")

question = st.chat_input("Ask a question about your indexed documents")
if question:
    with st.chat_message("user"):
        st.write(question)
    sources = retrieve(question, get_store())
    if not sources:
        with st.chat_message("assistant"):
            st.write("I could not find that in the uploaded documents.")
        st.stop()
    try:
        llm = get_llm()
        with st.chat_message("assistant"):
            with st.spinner("Reading the relevant pages..."):
                st.write(answer_question(question, sources, llm))
    except LLMConfigurationError as error:
        st.error(str(error))
    except Exception:
        logger.exception("Answer generation failed")
        st.error("The answer service is unavailable. Check your provider key and try again.")
    with st.expander("Retrieved source chunks"):
        for source in sources:
            st.markdown(f"**{source.file_name}, page {source.page_number}**")
            st.caption(source.text)
