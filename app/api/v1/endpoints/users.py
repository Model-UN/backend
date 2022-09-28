from csv import DictWriter
from typing import List

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Body, Request
from fastapi.responses import StreamingResponse

from app.common.enumerations import Collections
from app.db.client import db
from app.db.dto.authorization_dto import AuthorizationDto
from app.db.dto.user_dto import UserDto
from app.settings import settings

router = APIRouter()
collection = Collections.USERS.value


@router.get(
    "/",
    response_description=f"List all {collection}",
    response_model=List[UserDto]
)
async def list_users(auth: AuthorizationDto = Body(...)):
    if not auth:
        return HTTPException(
            status_code=401
        )

    return await db[collection].find().to_list(1000)


@router.get(
    "/export",
    response_description=f"Flattens and exports {collection} to CSV",
)
async def export_users(request: Request):
    if not request.scope["aws.event"].get("queryStringParameters") or \
            not request.scope["aws.event"]["queryStringParameters"].get("authorization") or \
            request.scope["aws.event"]["queryStringParameters"]["authorization"] != settings.secret_key:
        return HTTPException(
            status_code=401
        )

    docs = await db[collection].find().to_list(1000)

    objs = []
    field_name_acc = []
    for doc in docs:
        user = UserDto.parse_obj(doc)

        user_application = user.application

        user_obj = {}
        user_obj.update({
            "id": user.id_,
            "First Name": user.first_name,
            "Last Name": user.last_name,
            "Email": user.email,
            "Phone Number": user.phone_number,
            "Date of Birth": user.date_of_birth.strftime("%Y-%m-%d")
        })
        user_obj.update(**user_application)
        objs.append(user_obj)

        field_name_acc.extend(user_obj.keys())

    field_names = []
    for field_name in field_name_acc:
        if field_name not in field_names:
            field_names.append(field_name)

    with open("users.csv", "w") as userscsv:
        writer = DictWriter(userscsv, fieldnames=field_names)
        writer.writeheader()
        for obj in objs:
            writer.writerow(obj)

    def iterfile():
        with open("users.csv", mode="rb") as userscsv:
            yield from userscsv

    response = StreamingResponse(iterfile(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=users.csv"
    return response


@router.get(
    "/{id_}",
    response_description=f"Get data for a single {collection}",
    response_model=UserDto,
)
async def get_user(id_: str, request: Request):
    if not request.scope["aws.event"].get("queryStringParameters") or \
            not request.scope["aws.event"]["queryStringParameters"].get("authorization") or \
            request.scope["aws.event"]["queryStringParameters"]["authorization"] != settings.secret_key:
        return HTTPException(
            status_code=401
        )

    doc = await db[collection].find_one({"_id": ObjectId(id_)})

    if doc is not None:
        return doc

    raise HTTPException(
        status_code=404,
        detail=f"{collection.title()} of id: {id_} not found."
    )
