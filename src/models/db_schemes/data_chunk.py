# =============================================================================
# models/db_schemes/data_chunk.py — Chunk & Retrieval Pydantic Schemas
# =============================================================================
# PURPOSE:
#   Two schemas live here:
#     1. DataChunk         — shape of a text chunk stored in MongoDB
#     2. RetrievalDocument — lightweight search result (text + similarity score)
#
# MongoDB collection: "chunks"
# Document shape for DataChunk:
#   {
#     "_id":              ObjectId("..."),
#     "chunk_text":       "Cache coherence ensures that...",
#     "chunk_metadata":   {"source": "lecture.pdf", "page": 3},
#     "chunk_order":      1,                    ← position in the original document
#     "chunk_project_id": ObjectId("64a3f...")  ← references the project
#   }
#
# USED BY:
#   ChunkModel, ProcessController, NlpController, QDrantDB
#
# TEAM NOTE (Pair A — both members):
#   DataChunk is the contract between Pair A (who creates chunks) and
#   Ahmed (who reads chunks for embedding). Agree on this schema on Day 1.
# =============================================================================

from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional, Dict, Any


class DataChunk(BaseModel):
    """
    Represents one text chunk stored in MongoDB.
    Created by ProcessController, consumed by NlpController.
    """

    id: Optional[str] = Field(None, alias="_id")
    chunk_text: str                          # the actual text content
    chunk_metadata: Dict[str, Any] = {}     # e.g. {"source": "file.pdf", "page": 2}
    chunk_order: int = 0                    # sequential position in the document
    chunk_project_id: Optional[str] = None  # ObjectId string of the parent project

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        populate_by_name = True


class RetrievalDocument(BaseModel):
    """
    Lightweight model for a single semantic search result.
    Returned by QDrantDB.search_by_vector() and consumed by NlpController.

    Fields:
        text:  The raw text content of the retrieved chunk
        score: Cosine similarity score in [0.0, 1.0] — higher is more relevant
    """
    text: str
    score: float
