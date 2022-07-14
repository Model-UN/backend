from typing import List

from bson import ObjectId
from fastapi import APIRouter, HTTPException

from app.common.enumerations import Collections
from app.db.client import db
from app.db.dto.conference_dto import ConferenceDto

router = APIRouter()
collection = Collections.CONFERENCES.value


@router.get(
    "/",
    response_description=f"List all {collection}",
    response_model=List[ConferenceDto]
)
async def list_conferences():
    return await db[collection].find().to_list(1000)


@router.get(
    "/{id_}",
    response_description=f"Get information for a single {collection}",
    response_model=ConferenceDto
)
async def get_conference(id_: str):
    doc = await db[collection].find_one({"_id": ObjectId(id_)})

    if doc is not None:
        return doc

    raise HTTPException(
        status_code=404,
        detail=f"{collection.title()} of id: {id_} not found."
    )
