from pydantic import BaseModel, Field, field_validator, ConfigDict
from bson import ObjectId
from typing import Optional
from datetime import datetime

class Project(BaseModel):

    id: Optional[str] = Field(None, alias="_id")
    project_id: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now()
    )

    @field_validator("project_id")
    @classmethod
    def project_id_must_be_alphanumeric(cls, v):
        v = v.strip().lower()
        if not v.isalnum():
            raise ValueError(
                f"project_id must contain only letters and digits (a-z, 0-9). "
                f"Received: '{v}'"
            )
        return v

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )