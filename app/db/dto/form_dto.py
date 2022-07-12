from typing import List, Optional

from pydantic import BaseModel, Field

from app.db.dto.base_dto import BaseDto
from app.db.dto.ext.object_id import ObjectId


class FormValueDto(BaseModel):
    id_: ObjectId = Field(default_factory=ObjectId, alias="_id")
    value: str = Field(...)


class FormFieldDto(BaseModel):
    id_: ObjectId = Field(default_factory=ObjectId, alias="_id")
    active: bool = Field(...)
    required: bool = Field(...)
    field_type: str = Field(...)
    content: str = Field(...)
    index: int
    description: Optional[str] = Field(...)
    values: Optional[List[FormValueDto]] = Field(...)


class FormSectionsDto(BaseModel):
    id_: ObjectId = Field(default_factory=ObjectId, alias="_id")
    active: bool = Field(...)
    title: str = Field(...)
    fields: List[FormFieldDto] = Field(...)
    subtitle: Optional[str] = Field(...)
    intro: Optional[str] = Field(...)
    outro: Optional[str] = Field(...)


class FormDto(BaseDto):
    active: bool
    sections: List[FormSectionsDto]
