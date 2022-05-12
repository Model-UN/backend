from datetime import datetime

from pydantic import BaseModel


class MUNDOBaseModel(BaseModel):
    created_at: datetime
    created_by: int
