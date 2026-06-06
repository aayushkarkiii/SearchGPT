# SearchGPT- AI Powered GPT


# Step 1: What Your Project Really Is
Your system is basically 3 things:

- **Chat system** (Gemini-powered brain)
- **Document Q&A system** (FAISS + PDF memory)
- **Simple UI** (Streamlit chat interface)

Everything else is optional decoration.

# Step 2: What Components You Actually Need
To make this work, you need:

- **UI layer** → Streamlit
- **Backend logic** → Python functions
- **LLM** → Gemini Flash API
- **Embeddings** → sentence-transformers
- **Vector DB** → FAISS
- **PDF processing** → PyMuPDF

That’s the entire ecosystem.

# Step 3: How Data Flows in Your System
You have two flows:

A) **Normal Chat Flow**
- User message → Gemini → response

B) **PDF Q&A Flow (RAG)**
- PDF → text extraction → chunking → embeddings → FAISS store
- Query → embedding → FAISS search → context → Gemini → response

# Step 4: What NOT to Include (Important)
To keep this stable:

- No React (for now)
- No login system
- No database (SQLite/Postgres unnecessary)
- No multi-agent AI systems
- No complex orchestration frameworks
> You are building a working AI assistant, not an AI company backend.

---
## 2. Solution (Project Overview)
🧠 **Project:** SearchGPT (Mini AI Chat + PDF Intelligence System)
📌 **1. Project Goal:**
Build a lightweight ChatGPT-like system that:
- Chats with users using Gemini Flash
- Accepts PDF uploads
- Answers questions from uploaded documents using semantic search (FAISS)
- Runs fully in Python with a simple UI
⚙️ **2. Tech Stack:**
### 🖥️ UI Layer:
Streamlit (Python-based UI framework)
Chat interface + file upload support.
### 🧠 AI / LLM Layer:
google Gemini 2.5 Flash (main LLM)
hugging Face (optional fallback models)
### 📄 Document Processing:
pymupdf (fitz) — extract text from PDFs.
txt chunking — split documents into small passages.
### 🔎 Embedding Model:
sentence-transformers,
e.g., all-MiniLM-L6-v2.
Used to convert text into vectors.
### 📦 Vector Database:
FAISS (Facebook AI Similarity Search):
stores embeddings,
promotes fast similarity search for relevant chunks.
---
## 3. System Architecture:
display diagram of architecture with components like Streamlit UI, Python Backend, Gemini LLM, FAISS Vector DB, and PDF Parser & Chunking.
---
## 4. Core Features:
a) **Chat System:**
b) User asks question,
gemini flash generates response,
note: no memory unless PDF used.
c) **PDF Intelligence (RAG System):**
upload PDF,
etract text,
split into chunks,
download chunks into embeddings,
stored in FAISS,
r retrieve relevant chunks for questions,
send context + query to Gemini.
d) **Semantic Search:** Finds meaning-based matches, not keyword-based; improves accuracy for PDF Q&A.
define project structure with directories and files like app.py, services/, vectorstore/, utils/ etc.
detail execution plan in phases from building chat system to polishing features like chat history and multiple PDFs.
define key design principles emphasizing simplicity, FAISS as memory not intelligence, Gemini as reasoning engine, Streamlit as UI only, and building a working version first.
describe final outcome including a ChatGPT-like interface powered by Gemini, PDF-based Q&A system, semantic search using FAISS, and a fully Python-based working app.

### Folder structure
SearchGPT/
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   ├── style.css
│
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│
│   ├── routes/
│   │   ├── chat.py
│   │   ├── upload.py
│
│   ├── services/
│   │   ├── gemini.py
│   │   ├── rag.py
│   │   ├── pdf.py
│   │   ├── embeddings.py
│
│   ├── utils/
│   │   ├── chunker.py
│
│   ├── vectorstore/
│   │   ├── faiss.index
│   │   ├── metadata.pkl
│
│
└── README.md