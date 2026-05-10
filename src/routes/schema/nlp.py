# =============================================================================
# routes/schema/nlp.py — Request Body Schemas for NLP Routes
# =============================================================================
# PURPOSE:
#   Defines the expected JSON body shapes for the /api/nlp/* endpoints.
#
# USED BY: routes/nlp.py
#
# TEAM NOTE (Pair B — Member 4):
#   PushDataRequest and SearchRequest are tiny — keep them minimal.
#   The heavy lifting is done by NlpController, not the schema.
# =============================================================================

from pydantic import BaseModel, Field,field_validator


class PushDataRequest(BaseModel):
    """
    Request body for POST /api/nlp/index/push/{project_id}

    Example JSON:
    {
        "do_reset": 0    ← 1 to delete the Qdrant collection and rebuild from scratch
    }
    """
    do_reset: int = Field(
        default=0,
        ge=0,
        le=1,
        description="Set to 1 to wipe and rebuild the vector index"
    )


class SearchRequest(BaseModel):
    """
    Request body for POST /api/nlp/index/search/{project_id}
    AND          for POST /api/nlp/index/answer/{project_id}

    Example JSON:
    {
        "text":     "What is cache coherence?",
        "top_k":    5,
        "language": "en"
    }
    """
    text: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="The search query or question to answer"
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of chunks to retrieve from the vector index"
    )
    language: str = Field(
        default="en",
        description="Response language: 'en' for English, 'ar' for Arabic"
    )

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str):

        value = value.strip()

        if not value:
            raise ValueError("Query text cannot be empty")
        return value

    @field_validator("language")
    @classmethod
    def validate_language(cls, value: str):

        allowed_languages = ["en", "ar"]

        value = value.lower().strip()

        if value not in allowed_languages:
            raise ValueError(
                f"Language must be one of {allowed_languages}"
            )

        return value
class PushDataResponse(BaseModel):
    """
    Response after indexing documents into vector DB
    """
    success: bool
    collection_name: str
    indexed_chunks: int
    message: str


class SearchResult(BaseModel):
    text: str
    score: float
    source: str


class SearchResponse(BaseModel):
    results: list[SearchResult]


class AnswerResponse(BaseModel):
    answer: str
    sources: list[str]


class InfoResponse(BaseModel):
    project_id: str
    collection_name: str
    total_chunks: int
    indexed: bool