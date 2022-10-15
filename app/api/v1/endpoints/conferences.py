from bson import ObjectId
from fastapi import APIRouter, HTTPException, Request

from app.common.enumerations import Collections
from app.db.client import db
from app.settings import settings

router = APIRouter()
collection = Collections.CONFERENCES.value


@router.get(
    "/",
    response_description=f"Get information for a single {collection}",
)
async def get_conference(request: Request):
    if not request.scope["aws.event"].get("queryStringParameters") or \
            not request.scope["aws.event"]["queryStringParameters"].get("authorization") or \
            request.scope["aws.event"]["queryStringParameters"]["authorization"] != settings.secret_key:
        return HTTPException(
            status_code=401
        )

    id_ = request.scope["aws.event"]["queryStringParameters"].get("id")

    if not id_:
        return await db[collection].find().to_list(1000)

    doc = await db[collection].find_one({"_id": ObjectId(id_)})

    if doc is not None:
        return doc

    raise HTTPException(
        status_code=404,
        detail=f"{collection.title()} of id: {id_} not found."
    )
