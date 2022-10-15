from datetime import datetime

from app.db.dto.base_dto import BaseDto
from app.db.dto.ext.models.location import Location


class ConferenceDto(BaseDto):
    name: str
    start_date: datetime
    end_date: datetime
    location: Location
    