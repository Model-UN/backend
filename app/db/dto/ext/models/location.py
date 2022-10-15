from typing import Optional

from app.db.dto.ext.object_id import BsonObjectId

from pydantic import BaseModel, Field


class Location(BaseModel):
    name: Optional[str] = Field(...)
    street_address: str = Field(...)
    city: str = Field(...)
    state: str = Field(...)
    country: str = Field(...)
    postal_code: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {BsonObjectId: str}
