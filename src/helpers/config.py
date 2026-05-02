# =============================================================================
# helpers/config.py — Application Configuration Layer
# =============================================================================
# PURPOSE:
#   Single source of truth for ALL configuration values used across the app.
#   Reads values from src/.env automatically using pydantic-settings.
#
# USED BY: Every layer — controllers, models, stores, routes.
#
# HOW IT WORKS:
#   Pydantic-settings reads the .env file and maps each KEY to a typed field.
#   If a required key is missing from .env, the app fails at startup with a
#   clear error message — no silent bugs.
#
# TEAM NOTE:
#   Never hardcode config values (API keys, URIs, model names) directly in
#   code. Always add a new field here and read it from .env instead.
# =============================================================================

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Loads and validates all environment variables from src/.env.
    Access any value with: get_settings().FIELD_NAME
    """

    # -- App identity --
    APP_NAME: str = "Mini-RAG"
    APP_VERSION: str = "0.1.0"

    # -- File upload validation --
    FILE_ALLOWED_EXTENSIONS: List[str] = ["text/plain", "application/pdf"]
    FILE_MAX_SIZE_MB: int = 10
    FILE_CHUNK_SIZE: int = 512000           # bytes read per aiofiles chunk during upload

    # -- MongoDB connection --
    MONGODB_URI: str                        # e.g. mongodb://admin:pass@localhost:27007
    MONGODB_DB_NAME: str = "mini_rag_db"

    # -- OpenAI-compatible LLM --
    OPENAI_API_KEY: str
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    GENERATE_RESPONSE_MODEL: str = "gpt-4o-mini"

    # -- Embedding model (local sentence-transformers) --
    EMBEDDINGS_MODEL: str = "BAAI/bge-small-en"
    EMBEDDING_DIMENSION: int = 384

    # -- LLM generation settings --
    MAX_INPUT_TOKENS: int = 1000
    MAX_RESPONSE_TOKENS: int = 500
    TEMPERATURE: float = 0.1

    # -- Qdrant vector database --
    VECTOR_DB_PATH: str = "assets/db/qdrant_data"
    VECTOR_DISTANCE_METRIC: str = "Cosine"

    class Config:
        env_file = ".env"                   # tells pydantic-settings where to look


def get_settings() -> Settings:
    """
    Factory function that creates a Settings instance.
    FastAPI routes use this with Depends(get_settings) for dependency injection.

    Example usage:
        from helpers.config import get_settings
        settings = get_settings()
        print(settings.APP_NAME)
    """
    return Settings()
