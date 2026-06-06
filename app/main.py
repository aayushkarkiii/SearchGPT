from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(title="SearchGPT")


    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes BEFORE mounting static files at `/`.
    # This prevents route matching issues where `/api/*` may be handled by static/fallback.
    app.include_router(router)
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")



    return app



app = create_app()

