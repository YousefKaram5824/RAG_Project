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

from pydantic import BaseModel, Field


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
