import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str
    gemini_model: str
    faiss_index_dir: str
    uploads_dir: str


def get_settings() -> Settings:
    gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Use project-local folders
    project_root = os.getenv("PROJECT_ROOT", os.getcwd())
    faiss_index_dir = os.path.join(project_root, "data", "vectorstore")
    uploads_dir = os.path.join(project_root, "data", "uploads")

    return Settings(
        gemini_api_key=gemini_api_key,
        gemini_model=gemini_model,
        faiss_index_dir=faiss_index_dir,
        uploads_dir=uploads_dir,
    )

