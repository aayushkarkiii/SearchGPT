from app.core.llm import generate_answer


def answer_chat(question: str) -> str:
    prompt = (
        "You are SearchGPT, a helpful assistant. "
        "Answer the user clearly and concisely.\n\n"
        f"User: {question}\n\nAssistant:"
    )
    return generate_answer(prompt)

