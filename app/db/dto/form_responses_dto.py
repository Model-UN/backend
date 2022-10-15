from typing import Any, Dict, List

from pydantic import BaseModel, Field

from app.db.dto.base_dto import BaseDto
from app.db.dto.ext.object_id import ObjectId


class FormResponse(BaseModel):
    id_: ObjectId = Field(default_factory=ObjectId, alias="_id")
    response: Any

    class Config:
        json_encoders = {ObjectId: str}


class FormResponsesDto(BaseModel):
    """
    The DTO for form POST requests
    """
    responses: List[FormResponse] = Field(...)


class FormResponses(BaseDto):
    """
    The object for which forms are inserted to Mongo
    """
    form_id: ObjectId
    responses: Dict[str, str] = Field(default_factory=dict)
