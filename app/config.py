"""Application configuration.

Settings are loaded from environment variables (and a local .env file in
development). See `.env.example` for the full list of supported variables.
"""

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Provider credentials -------------------------------------------------
    google_api_key: SecretStr = SecretStr("")
    tavily_api_key: SecretStr = SecretStr("")

    # --- Model selection ------------------------------------------------------
    llm_model: str = "gemini-2.5-flash"
    llm_temperature: float = 0.2

    # --- Research behaviour ---------------------------------------------------
    max_search_results: int = 5
    max_validation_attempts: int = 3
    confidence_threshold: int = 6

    # --- Server ---------------------------------------------------------------
    host: str = "0.0.0.0"
    port: int = 8000


settings = Settings()

# Handy for spotting misconfiguration during local development.
print(f"[config] settings loaded: {settings.model_dump()}")
