# MediGuide — Medical Chatbot

MediGuide is a lightweight local medical Q&A web app that uses a prebuilt FAISS vector index and generative model to answer user questions from a collection of medical PDFs. The UI is a small Flask app that sends user questions to a server, which retrieves related document chunks and asks the configured generative model to produce an answer using only the retrieved context.

## Key features

- Flask-based chat UI (`templates/chat.html`, `static/style.css`).
- Retrieval from a FAISS vector index stored in `faiss_medical_index/`.
- Local HuggingFace embeddings (configured in `src/helper.py`).
- Uses Google Generative AI SDK (via `from google import genai`) for response generation.

## Repository structure (important files)

- `app.py` — Flask app and main entrypoint. Exposes `/` and `/get` endpoints.
- `storeIndex.py` — (helper) script that references the helper utilities and shows index usage.
- `src/helper.py` — PDF loading, text splitting, and embedding creation.
- `src/prompt.py` — default system prompt template (also referenced in `app.py`).
- `faiss_medical_index/` — prebuilt FAISS index directory (contains `index.faiss`).
- `data/` — folder for PDF source documents used to create or rebuild the index.
- `templates/` and `static/` — UI files for the chat frontend.

## Prerequisites

- Windows machine (this repository was prepared on Windows). PowerShell commands are shown below.
- Python 3.10+ recommended.
- A Google Generative AI API key. Set it in the `.env` file (see below).
- If you plan to rebuild the FAISS index locally, you need an embeddings backend. `src/helper.py` currently uses a local HuggingFace model path. Make sure the model is available or change to a model id.

Notes on FAISS and Windows: installing `faiss` on Windows via pip can be tricky. Using conda is typically the easiest approach for FAISS:

- conda (recommended): `conda install -c conda-forge faiss-cpu`
- pip: you may find prebuilt wheels, but results vary across Python versions.

## Recommended Python packages

Create a virtual environment and install dependencies. The exact package names/versions may vary by environment. Recommended packages include:

- flask
- python-dotenv
- langchain
- langchain-community
- google-generative-ai
- sentence-transformers
- transformers
- faiss-cpu (or use conda)

Example (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install flask python-dotenv langchain langchain-community google-generative-ai sentence-transformers transformers
# Install FAISS via conda if possible:
# conda install -c conda-forge faiss-cpu
```

If you prefer, create a `requirements.txt` with the pinned versions for your environment and install via `pip install -r requirements.txt`.

## Environment configuration

Copy `.env` and set your Google API key (the repository includes a `.env` with the variable name):

```powershell
# Windows PowerShell
code .env   # or edit with your preferred editor
# in .env set:
# GOOGLE_API_KEY=YOUR_API_KEY_HERE
```

`app.py` sets the environment variable for the running process from `.env`:

```python
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
```

## Model / Embeddings

`src/helper.py` currently uses a local path for the embeddings model:

```python
model_name = r"D:\sent transformres\all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(model_name=model_name)
```

If you do not have a local copy at that path, either download the model there or change `model_name` to the HuggingFace model id such as:

```python
model_name = "sentence-transformers/all-MiniLM-L6-v2"
```

Note: when using remote HF models, you may need `huggingface_hub` credentials or internet access.

## Rebuilding the FAISS index (optional)

If you want to rebuild the FAISS index from PDFs in `data/`, you can adapt the following snippet into `storeIndex.py` or run it from a script:

```python
from src.helper import load_pdf_files, filter_to_minimal_docs, text_split, download_embeddings
from langchain_community.vectorstores import FAISS

# load PDFs
extracted = load_pdf_files(data='data/')
minimal = filter_to_minimal_docs(extracted)
chunks = text_split(minimal)
embeddings = download_embeddings()
# create the index from documents (chunks is a list of langchain Document objects)
faiss_index = FAISS.from_documents(chunks, embeddings)
# save locally for the app to use
faiss_index.save_local("faiss_medical_index")
```

Run this after populating `data/` with your PDFs. It will create/overwrite the `faiss_medical_index/` directory used by the app.

## Run the app (development)

From the project root, with your virtual environment activated and `.env` set:

```powershell
python .\app.py
```

This will start Flask on port 5000 by default (see `app.run(debug=True, port=5000)` in `app.py`). Open:

http://127.0.0.1:5000/

### Example: call the `/get` endpoint from PowerShell

```powershell
# Replace the message value as needed
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:5000/get" -ContentType 'application/json' -Body (@{ message = "What is hypertension?" } | ConvertTo-Json)
```

The server expects a JSON payload with a `message` field and returns JSON like `{"answer":"..."}`.

## Prompt & Response behavior

`app.py` builds a system prompt that instructs the model to use only the retrieved context to answer the question. If you want to tune how the assistant responds, edit `system_prompt` in `app.py` or the separate `src/prompt.py`.

## Troubleshooting

- FAISS errors on Windows: prefer installing via conda (`conda install -c conda-forge faiss-cpu`) or use a Linux/macOS environment.
- Embeddings model path: ensure `src/helper.py` points to a valid model path or model id.
- Google generative API errors: confirm `GOOGLE_API_KEY` in `.env` and that the SDK package is installed and compatible.
- If no search results are returned, verify `faiss_medical_index/index.faiss` exists and was created with the same embeddings configuration used at runtime (embedding model must match when creating and loading the index).

## Extending or customizing

- Swap the generation model or model parameters inside `app.py` when calling `client.models.generate_content`.
- Add caching for repeated queries.
- Add user authentication if exposing the server publicly.

## License

This project is provided as-is for development and demonstration purposes. Add an explicit license if you plan to share or publish.

---

If you'd like, I can also:

- Generate a `requirements.txt` with recommended pinned versions for your environment.
- Add a simple script to rebuild the FAISS index automatically and save it.
- Update `storeIndex.py` to actually write the index instead of loading it, if you want that behavior.

Tell me which of these you'd like next.
