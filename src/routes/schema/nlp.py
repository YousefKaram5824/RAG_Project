from pydantic import BaseModel, Field,field_validator

class PushDataRequest(BaseModel):

    do_reset: int = Field(
        default=0,
        ge=0,
        le=1,
        description="Set to 1 to wipe and rebuild the vector index"
    )


class SearchRequest(BaseModel):

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
    source_file: str = Field(
        default=None,
        description="Optional filename filter — restricts retrieval to chunks from this document only (e.g., 'Python_Full-Stack_Developer.pdf')"
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