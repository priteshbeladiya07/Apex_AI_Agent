import os

from langchain_mistralai import ChatMistralAI


def create_mistral_llm(
    model: str | None = None,
    temperature: float = 0.2,
) -> ChatMistralAI:
    api_key = os.getenv("MISTRAL_API_KEY")

    if not api_key:
        raise ValueError(
            "MISTRAL_API_KEY is missing. Add it to your .env file."
        )

    return ChatMistralAI(
        model=model or os.getenv("MISTRAL_MODEL", "codestral-2508"),
        api_key=api_key,
        temperature=temperature,
        max_retries=2,
        timeout=60,
    )
