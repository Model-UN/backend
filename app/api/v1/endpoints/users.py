from typing import List

from bson import ObjectId
from fastapi import APIRouter, HTTPException

from app.common.enumerations import Collections
from app.db.client import db
from app.db.dto.user_dto import UserDto

router = APIRouter()
collection = Collections.USERS.value


@router.get(
    "/",
    response_description=f"List all {collection}",
    response_model=List[UserDto]
)
async def list_users():
    return await db[collection].find().to_list(1000)


@router.get(
    "/{id_}",
    response_description=f"Get data for a single {collection}",
    response_model=UserDto
)
async def get_user(id_: str):
    doc = await db[collection].find_one({"_id": ObjectId(id_)})

    if doc is not None:
        return doc

    raise HTTPException(
        status_code=404,
        detail=f"{collection.title()} of id: {id_} not found."
    )
