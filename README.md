# SearchGPT

A focused, single-process AI assistant that combines direct LLM chat with two Retrieval-Augmented Generation (RAG) pipelines — one for uploaded PDF documents and one for live webpages.

---

## Purpose

This project exists to answer one question clearly:

> How do you build a working RAG system from scratch, step by step, without unnecessary complexity?

It is not a generic chatbot wrapper. Every component has a specific responsibility, and the code is meant to be readable, traceable, and understandable by someone learning how RAG works in practice.

---

## Stack

| Layer | Technology |
|---|---|
| Web Framework | FastAPI |
| ASGI Server | Uvicorn |
| LLM | Google Gemini 2.5 Flash |
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`) |
| Vector Store | FAISS (IndexFlatIP, cosine similarity) |
| PDF Parsing | PyMuPDF (`pymupdf`) |
| HTTP Client | `httpx` (async, for URL fetch) |
| Config | `python-dotenv` |
| Package Manager | `uv` |
| Frontend | HTML + Vanilla JS + TailwindCSS (CDN) |

---

## Project Structure

```
Project/
├── app/
│   ├── main.py                  # FastAPI app factory, mounts routes + static files
│   ├── api/
│   │   └── routes.py            # HTTP endpoints: /api/chat, /api/pdf/ask, /api/url/ask
│   ├── core/
│   │   ├── config.py            # Loads .env, returns frozen Settings dataclass
│   │   └── llm.py               # Calls Gemini API with a given prompt string
│   └── services/
│       ├── chat_service.py      # Builds prompt for plain chat, calls llm.py
│       ├── pdf_service.py       # PDF text extraction + character-based chunking
│       ├── url_service.py       # Fetches webpage HTML, strips tags, returns clean text
│       ├── embedding_service.py # Wraps SentenceTransformer, returns normalized vectors
│       ├── vector_service.py    # FAISS index build/load/save/query (PDF + text paths)
│       └── rag_service.py       # Full RAG pipelines for PDF and URL contexts
├── frontend/
│   ├── index.html               # Single-page UI
│   └── script.js                # Calls backend APIs, manages URL context state
├── data/
│   └── vectorstore/             # Persisted FAISS indexes (auto-created at runtime)
├── .env                         # API key (not committed)
├── .env.example                 # Template
├── requirements.txt             # Pinned dependencies
└── pyproject.toml               # uv project manifest
```

---

## How It Works

### Flow 1 — Direct Chat

The simplest path. No retrieval involved.

```
User types question
    → POST /api/chat
    → chat_service.py builds a system + user prompt
    → llm.py calls Gemini API
    → Answer returned to frontend
```

### Flow 2 — PDF RAG Pipeline

```
User uploads PDF + question
    → POST /api/pdf/ask
    → pdf_service.extract_pdf_text()
          reads pages via PyMuPDF, joins text
    → pdf_service.chunk_text()
          splits into ~800 char chunks with 150 char overlap
    → embedding_service.embed_texts()
          encodes chunks → float32 vectors (normalized)
    → faiss.IndexFlatIP built, saved to data/vectorstore/<sha256>.index
    → On next upload of same PDF, index is loaded from disk (cache hit)
    → embedding_service.embed_texts([question])
    → FAISS .search() returns top-5 nearest chunk indices
    → Retrieved chunks assembled into context block
    → llm.py called with context + question prompt
    → Answer + source previews returned
```

### Flow 3 — Webpage URL RAG Pipeline

Same as PDF flow, but text comes from a live URL.

```
User sets a URL context + types question
    → POST /api/url/ask
    → url_service.extract_url_text(url)
          httpx fetches HTML (async)
          html.parser strips script/style/nav tags
          returns clean text string
    → vector_service.build_or_load_text(text, seed=url)
          sha256 of URL used as doc_id
          same chunking + FAISS build/load logic as PDF path
    → Top-5 chunks retrieved via FAISS search
    → llm.py called with webpage context + question
    → Answer returned
```

### Caching Behavior

Both RAG pipelines hash the source content (PDF bytes → sha256, URL string → sha256) and save the FAISS index and chunk metadata to `data/vectorstore/`. On repeated queries for the same document, the index is loaded from disk rather than rebuilt.

---

## Running the Project

### Prerequisites
- Python 3.11+
- `uv` installed (`pip install uv` or `winget install astral-sh.uv`)
- A Google Gemini API key

### Setup

```bash
# 1. Clone or navigate to the project
cd Project

# 2. Install dependencies (uv creates .venv automatically)
uv add -r requirements.txt

# 3. Configure environment
copy .env.example .env
# Edit .env and add your key:
# GEMINI_API_KEY=your_key_here

# 4. Run the server
uv run uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000` in your browser.

---

## Module Responsibilities (Quick Reference)

| File | Does One Thing |
|---|---|
| `config.py` | Reads env vars, returns typed `Settings` |
| `llm.py` | Takes a prompt string, returns Gemini response string |
| `chat_service.py` | Builds the chat prompt, calls `llm.py` |
| `pdf_service.py` | Extract text from PDF bytes, chunk text |
| `url_service.py` | Fetch + clean text from a webpage URL |
| `embedding_service.py` | Convert text list → float32 numpy vectors |
| `vector_service.py` | Build, save, load, and query FAISS indexes |
| `rag_service.py` | Orchestrate retrieval → prompt building → LLM call |
| `routes.py` | Map HTTP requests to the right service functions |
| `main.py` | Wire together FastAPI app, CORS, routes, static files |

---

## Design Decisions

**Why FAISS instead of a vector database?**
No running server required. For single-user or prototype scale, a saved `.index` file is simpler and sufficient. Swapping to Pinecone, Qdrant, or Weaviate later only requires changing `vector_service.py`.

**Why character-based chunking?**
Predictable, dependency-free, easy to reason about. Sentence-aware chunking (spaCy, NLTK) is an obvious upgrade when retrieval quality needs to improve.

**Why `html.parser` instead of BeautifulSoup?**
Zero extra dependency. The built-in parser is enough for stripping tags and extracting visible text for prototype-level quality.

**Why a flat module structure under `services/`?**
Each file has a single responsibility and no circular imports. Adding a new RAG source (YouTube transcript, DOCX, CSV) means adding one new `*_service.py` file and one new route — no existing code changes.

---

## Future Enhancements

These are not blockers. They are the logical next steps if the project grows.

### Retrieval Quality
- [ ] Replace character chunking with sentence-aware or semantic chunking
- [ ] Add re-ranking step (cross-encoder) after initial FAISS retrieval
- [ ] Experiment with larger embedding models (`all-mpnet-base-v2`)

### Memory & Context
- [ ] Add conversation memory to the chat flow (sliding window of recent turns)
- [ ] Support multi-document RAG (index multiple PDFs together)

### Infrastructure
- [ ] Replace in-process FAISS with a persistent vector DB (Qdrant, Weaviate)
- [ ] Add async PDF ingestion endpoint (background task + status polling)
- [ ] Add request-level error handling middleware returning consistent JSON errors

### Frontend
- [ ] Add PDF upload UI in addition to URL context
- [ ] Display source chunks used for each answer
- [ ] Add markdown rendering for LLM responses

### Ops
- [ ] Add structured logging (replace uvicorn default logs)
- [ ] Add basic auth or API key guard on endpoints
- [ ] Containerize with Docker for consistent deployments

---

## Notes

- `GEMINI_API_KEY` is read at request time, not at startup. The app starts cleanly without it — errors surface only when an actual request hits the LLM.
- FAISS indexes are saved per document hash. Deleting `data/vectorstore/` clears all cached indexes and forces a rebuild on next query.
- The frontend is served as static files by FastAPI itself. No separate web server is needed.
