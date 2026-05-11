# =============================================================================
# routes/schema/data.py — Request Body Schemas for Data Routes
# =============================================================================
# PURPOSE:
#   Defines the expected JSON body shape for the /api/data/* endpoints.
#   FastAPI validates incoming requests against these schemas automatically.
#   If the client sends the wrong field types, FastAPI returns a 422 error.
#
# USED BY: routes/data.py
#
# TEAM NOTE (Pair B — Member 4):
#   These are the public API contracts. If you change a field name,
#   the Streamlit UI (interface.py) and the Tech Report must be updated too.
# =============================================================================

from pydantic import BaseModel, Field,field_validator


class RequestProcess(BaseModel):
    """
    Request body for POST /api/data/process/{project_id}

    Example JSON:
    {
        "project_id":   "resume.pdf",    ← filename to process inside the project folder
        "chunk_size":   500,             ← characters per chunk
        "overlap":      50,              ← characters of overlap between chunks
        "do_reset":     0                ← 1 to delete existing chunks first
    }
    """

    project_name: str = Field(
        ...,
        description="The filename to process, e.g. 'lecture.pdf'"
    )
    chunk_size: int = Field(
        default=500,
        ge=100,                          # minimum 100 chars — smaller is useless
        le=2000,                         # maximum 2000 chars
        description="Target chunk size in characters"
    )
    overlap: int = Field(
        default=50,
        ge=0,
        le=200,
        description="Overlap between consecutive chunks in characters"
    )
    do_reset: int = Field(
        default=0,
        ge=0,
        le=1,
        description="Set to 1 to delete existing chunks before processing"
    )
    @field_validator("project_name")
    @classmethod
    def validate_filename(cls, value:str):
        value = value.strip()
        if not value:
            raise ValueError("Filename cannot be empty")
        return value

    @field_validator("overlap")
    @classmethod
    def validate_overlap(cls, overlap: int, info):

        chunk_size = info.data.get("chunk_size")

        if chunk_size and overlap >= chunk_size:
            raise ValueError(
                "Overlap must be smaller than chunk_size"
            )
        return overlap
class ProcessResponse(BaseModel):
    success: bool
    message: str
    filename: str
    chunks_created: int


class UploadResponse(BaseModel):
    success: bool
    filename: str
    size_bytes: int
    message: str