from langchain_core.language_models import BaseChatModel

from apex_ai.llm.mistral import create_mistral_llm


def get_llm(
    provider: str = "mistral",
    model: str | None = None,
    temperature: float = 0.2,
) -> BaseChatModel:
    if provider.lower() == "mistral":
        return create_mistral_llm(
            model=model,
            temperature=temperature,
        )

    raise ValueError(
        f"Unsupported LLM provider: {provider}. "
        "Currently supported: mistral"
    )
