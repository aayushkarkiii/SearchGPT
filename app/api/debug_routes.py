from fastapi import APIRouter, Form

router = APIRouter()


@router.api_route("/debug/methods", methods=["*"])
def debug_methods(path: str = "", method: str = "", question: str = Form(None)):
    # Simple echo for debugging. If hit, server routing is correct.
    return {
        "path": path,
        "method": method,
        "question": question,
    }

