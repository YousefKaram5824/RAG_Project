from pydantic import BaseModel, Field, field_validator, ConfigDict
from bson import ObjectId
from typing import Optional, Dict, Any

class DataChunk(BaseModel):
    
    id: Optional[str] = Field(None, alias="_id")
    chunk_text: str
    chunk_metadata: Dict[str, Any] = Field(default_factory=dict)    # {"source": "file.pdf", "page": 2}
    chunk_order: int = 0                    # sequential position in the document
    chunk_project_id: Optional[str] = None  # foreign key 

    @field_validator("id", "chunk_project_id", mode="before")
    @classmethod
    def coerce_object_id_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v
    
    def to_mongo_dict(self) -> dict:
        data = self.model_dump(by_alias=True, exclude_none=True)
        data.pop("_id", None)
        return data
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )

class RetrievalDocument(BaseModel):
    text: str
    score: float