from typing import List, Tuple

from fastapi import UploadFile

from app.core.llm import generate_answer
from app.services.vector_service import build_or_load_index_for_upload, vector_service_singleton
from app.services.pdf_service import extract_pdf_text


async def answer_with_rag(pdf: UploadFile, question: str) -> Tuple[str, List[str]]:
    pdf_bytes = await pdf.read()

    # Build/load index for this specific PDF upload
    _doc_id, index, chunks = build_or_load_index_for_upload(pdf_bytes)

    # Retrieve relevant chunks
    contexts = vector_service_singleton.query(question, index, chunks, top_k=5)

    context_block = "\n\n---\n\n".join(contexts)

    prompt = (
        "You are SearchGPT. Use ONLY the provided PDF context to answer. "
        "If the context is insufficient, say you don't know.\n\n"
        f"Question: {question}\n\n"
        f"PDF Context:\n{context_block}\n\n"
        "Answer (include brief reasoning implicitly, but keep output concise):"
    )

    answer = generate_answer(prompt)

    # Provide “sources” as chunk previews for prototype
    sources = [c[:250].replace("\n", " ") + ("..." if len(c) > 250 else "") for c in contexts]
    return answer, sources


async def answer_with_rag_url(url: str, question: str) -> Tuple[str, List[str]]:
    from app.services.url_service import extract_url_text
    from app.services.vector_service import build_or_load_index_for_text

    # Extract text from webpage URL
    url_text = await extract_url_text(url)

    # Build or load index for this webpage
    _doc_id, index, chunks = build_or_load_index_for_text(url_text, doc_id_seed=url)

    # Retrieve relevant chunks
    contexts = vector_service_singleton.query(question, index, chunks, top_k=5)

    context_block = "\n\n---\n\n".join(contexts)

    prompt = (
        "You are SearchGPT. Use ONLY the provided webpage context to answer. "
        "If the context is insufficient, say you don't know.\n\n"
        f"Question: {question}\n\n"
        f"Webpage Context:\n{context_block}\n\n"
        "Answer (include brief reasoning implicitly, but keep output concise):"
    )

    answer = generate_answer(prompt)

    # Provide sources
    sources = [c[:250].replace("\n", " ") + ("..." if len(c) > 250 else "") for c in contexts]
    return answer, sources

