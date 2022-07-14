from typing import Any, List

from pydantic import BaseModel, Field

from app.db.dto.ext.object_id import ObjectId


class FormResponse(BaseModel):
    id_: ObjectId = Field(default_factory=ObjectId, alias="_id")
    response: Any

    class Config:
        json_encoders = {ObjectId: str}


class FormResponsesDto(BaseModel):
    responses: List[FormResponse] = Field(...)
