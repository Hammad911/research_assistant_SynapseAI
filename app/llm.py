"""LLM factory.

Centralises model construction so every agent talks to the same provider and
model configuration. Swap the provider here if you change vendors.
"""

from langchain_openai import ChatOpenAI

from app.config import settings


def get_llm(temperature: float | None = None) -> ChatOpenAI:
    """Return a chat model configured from application settings."""
    return ChatOpenAI(
        model=settings.llm_model,
        temperature=settings.llm_temperature if temperature is None else temperature,
        api_key=settings.openai_api_key,
    )
