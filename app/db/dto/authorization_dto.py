from typing import Optional

from pydantic import BaseModel

from app.settings import settings


class QueryStringParameters(BaseModel):
    authorization: Optional[str]


class AuthorizationDto(BaseModel):
    queryStringParameters: Optional[QueryStringParameters]

    def __bool__(self):
        return self.queryStringParameters.authorization == settings.secret_key
