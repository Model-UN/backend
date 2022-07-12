from datetime import datetime
from typing import Optional, Union

from bson import ObjectId as BsonObjectId
from pydantic import BaseModel, Field

from app.db.dto.ext.object_id import ObjectId


class BaseDto(BaseModel):
    id_: ObjectId = Field(default_factory=ObjectId, alias="_id")
    updated_by: Optional[Union[ObjectId, str]] = Field(...)
    updated_on: Optional[datetime] = Field(default=datetime.utcnow())
    created_by: Optional[Union[ObjectId, str]] = Field(...)
    created_on: Optional[datetime] = Field(datetime.utcnow())

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {BsonObjectId: str}
