from typing import Optional

from app.core.config import get_settings


def generate_answer(prompt: str) -> str:
    """Generate an answer using Gemini.

    Note: keep imports inside the function so the app can start even if the
    Gemini dependency/credential is missing.
    """

    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError("Missing GEMINI_API_KEY in environment/.env")

    try:
        import google.generativeai as genai
    except ModuleNotFoundError as e:
        raise RuntimeError(
            "Missing dependency google-generativeai. Run: pip install google-generativeai"
        ) from e

    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(settings.gemini_model)
    resp = model.generate_content(prompt)
    return getattr(resp, "text", "").strip()


