# Deployment

## Streamlit Community Cloud

1. Push this repository to GitHub.
2. In Streamlit Community Cloud, create an app from the repository, branch `main`, and file `app.py`.
3. In Advanced settings, add `LLM_PROVIDER` and either `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` as secrets.
4. Deploy. The local Chroma directory is ephemeral on Community Cloud, so users need to index PDFs again after a restart.

## Hugging Face Spaces

1. Create a new Space with the Streamlit SDK and push this repository to it.
2. Set the Space's app file to `app.py` and install from `requirements.txt`.
3. Add `LLM_PROVIDER` plus the matching API key in the Space Settings secrets panel.
4. Use a persistent storage upgrade if the index must survive a Space restart; otherwise the local index is temporary.
