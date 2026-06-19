"""LLM factory.

Centralises model construction so every agent talks to the same provider and
model configuration. Swap the provider here if you change vendors.
"""

from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import settings
from app.logger import SensitiveLogCallbackHandler


def get_llm(temperature: float | None = None) -> ChatGoogleGenerativeAI:
    """Return a chat model configured from application settings."""
    return ChatGoogleGenerativeAI(
        model=settings.llm_model,
        temperature=settings.llm_temperature if temperature is None else temperature,
        api_key=settings.google_api_key.get_secret_value(),
        callbacks=[SensitiveLogCallbackHandler()],
    )
