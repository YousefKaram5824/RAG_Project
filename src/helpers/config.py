from pydantic_settings import BaseSettings,SettingsConfigDict
from typing import List


class Settings(BaseSettings):

    # prepeare .env variables with default values

    APP_NAME: str = "Mini-RAG"
    APP_VERSION: str = "0.1.0"

    FILE_ALLOWED_EXTENSIONS: List[str] = ["text/plain", "application/pdf"]
    FILE_MAX_SIZE_MB: int = 10
    FILE_CHUNK_SIZE: int = 512000

    MONGODB_URI: str
    MONGODB_DB_NAME: str = "mini_rag_db"

    GROQ_API_KEY: str
    GROQ_API_BASE: str = "https://api.groq.com/openai/v1"
    GENERATE_RESPONSE_MODEL: str = "llama-3.1-8b-instant"
    ALT_GENERATE_RESPONSE_MODEL: str = "llama3-70b-8192"

    EMBEDDINGS_MODEL: str = "BAAI/bge-small-en"
    EMBEDDING_DIMENSION: int = 384

    MAX_INPUT_TOKENS: int = 1000
    MAX_RESPONSE_TOKENS: int = 500
    TEMPERATURE: float = 0.1

    VECTOR_DB_URL: str = "http://qdrant:6333"
    VECTOR_DB_PATH: str = "assets/db/qdrant_data"
    VECTOR_DISTANCE_METRIC: str = "Cosine"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


def get_settings() -> Settings:
    return Settings()
