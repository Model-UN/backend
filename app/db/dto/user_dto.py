import datetime
from typing import Any, Dict, Optional

from pydantic import Field

from app.db.dto.base_dto import BaseDto


class UserDto(BaseDto):
    first_name: str = Field(...)
    last_name: str = Field(...)
    date_of_birth: datetime.datetime = Field(...)
    email: str = Field(...)
    application: Dict[str, Any] = Field(...)
    phone_number: Optional[str] = Field(...)
