from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse

from app.services.rag_service import answer_with_rag, answer_with_rag_url
from app.services.chat_service import answer_chat



router = APIRouter()


@router.post("/api/chat", include_in_schema=True)
def chat_endpoint(question: str = Form(...)):

    answer = answer_chat(question)
    return {"answer": answer}




@router.post("/api/pdf/ask")
async def pdf_ask_endpoint(pdf: UploadFile = File(...), question: str = Form(...)):
    # Build/load FAISS index for this upload and ask with RAG
    answer, sources = await answer_with_rag(pdf, question)
    return {"answer": answer, "sources": sources}


@router.post("/api/url/ask")
async def url_ask_endpoint(url: str = Form(...), question: str = Form(...)):
    # Build/load FAISS index for this URL and ask with RAG
    answer, sources = await answer_with_rag_url(url, question)
    return {"answer": answer, "sources": sources}


@router.get("/debug/frontend")
def debug_frontend():
    # Quick sanity-check for static file sizes/content.
    # Useful when the browser shows a white screen.
    import os

    idx_path = os.path.join(os.getcwd(), "frontend", "index.html")
    js_path = os.path.join(os.getcwd(), "frontend", "script.js")

    def read_preview(p: str, n: int = 200) -> str:
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(n)
        except Exception as e:
            return f"<error reading {p}: {e}>"

    try:
        idx_size = os.path.getsize(idx_path)
    except Exception as e:
        idx_size = None

    try:
        js_size = os.path.getsize(js_path)
    except Exception as e:
        js_size = None

    return JSONResponse(
        {
            "index_html": {"path": idx_path, "size": idx_size, "preview": read_preview(idx_path)},
            "script_js": {"path": js_path, "size": js_size, "preview": read_preview(js_path)},
        }
    )


