import datetime
from csv import DictWriter
from typing import List

import requests
from bson import ObjectId
from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import StreamingResponse
from pymongo.results import InsertOneResult

from app.common.enumerations import Collections
from app.db.client import db
from app.db.dto.form_dto import FormDto, FormFieldDto
from app.db.dto.form_responses_dto import FormResponsesDto, FormResponses
from app.db.dto.user_dto import UserDto
from app.settings import settings

router = APIRouter()
collection = Collections.FORMS.value


@router.get(
    "/{id_}",
    response_description=f"Get data for a single {collection}",
    response_model=FormDto
)
async def get_form(id_: str):
    if id_ == "apply":  # funky staff app workaround logic
        id_ = settings.staff_application_id

    doc = await db[collection].find_one({"_id": ObjectId(id_)})

    if doc is not None:
        return doc

    raise HTTPException(
        status_code=404,
        detail=f"{collection.title()} of id: {id_} not found."
    )


@router.get(
    "/{id_}/export",
    response_description=f"Export {Collections.FORM_RESPONSES.value} for form of _id 'id_' as csv",
)
async def export_forms(id_: str):
    docs = await db[Collections.FORM_RESPONSES.value].find({"form_id": ObjectId(id_)}).to_list(1000)

    objs = []
    field_names = []
    for doc in docs:
        form = FormResponses.parse_obj(doc)

        for key in form.responses.keys():
            if key not in field_names:
                field_names.append(key)

        objs.append(form.responses)

    with open("responses.csv", "w") as csv_file:
        writer = DictWriter(csv_file, fieldnames=field_names)
        writer.writeheader()
        for obj in objs:
            writer.writerow(obj)

    def iterfile():
        with open("responses.csv", mode="rb") as csv_file_rb:
            yield from csv_file_rb

    response = StreamingResponse(iterfile(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=responses.csv"
    return response


@router.post(
    "/apply",
    response_description=f"Uses a {collection} as a *staff application*. That is, takes in a form submission and uses"
                         f"custom logic to create a user instead.",
)
async def apply(request: FormResponsesDto = Body(...)):
    """
    This POST handles user creation as well. It's insane as it is not exactly RESTful,
    but it will do. Eventually, we will want to move this whole deal elsewhere, but
    for now, this is what we have going on.

    :param request:
    :return:
    """
    # Get original form user filled out
    form = FormDto.parse_obj(await db[collection].find_one({"_id": ObjectId(settings.staff_application_id)}))
    # Get fields of that form
    fields = form.sections[0].fields

    response_map = {}
    for response in request.responses:
        response_map[response.id_] = response.response

    user_id = ObjectId()
    user_dict = {
        "_id": user_id,
        "first_name": None,
        "last_name": None,
        "date_of_birth": None,
        "email": None,
        "phone_number": None,
        "updated_by": user_id,
        "created_by": user_id,
        "application": {},
    }
    is_directorate_app = False

    for field in fields:
        user_response = response_map.get(field.id_)
        if user_response:
            content_lowered = field.content.lower()
            if content_lowered.startswith("first name"):
                user_dict["first_name"] = user_response
            elif content_lowered.startswith("surname"):
                user_dict["last_name"] = user_response
            elif content_lowered.startswith("date of birth"):
                user_dict["date_of_birth"] = datetime.datetime.strptime(user_response, "%Y-%m-%dT%H:%M:%S.%fZ")
            elif content_lowered.startswith("email"):
                user_dict["email"] = user_response
            elif content_lowered.startswith("phone number"):
                user_dict["phone_number"] = user_response
            else:
                user_dict["application"][field.content] = None
                if not user_response:
                    pass
                elif isinstance(user_response, str):
                    if ObjectId().is_valid(user_response):
                        response_id = ObjectId(user_response)
                        for value in field.values:
                            if value.id_ == response_id:
                                user_dict["application"][field.content] = value.value
                                if "directorate" in content_lowered and value.value.lower() == "yes":
                                    is_directorate_app = True
                    else:
                        user_dict["application"][field.content] = user_response
                elif isinstance(user_response, list):
                    value_list = []
                    for item in user_response:
                        if ObjectId().is_valid(item):
                            response_id = ObjectId(item)
                            for value in field.values:
                                if value.id_ == response_id:
                                    value_list.append(value.value)
                                    break
                        else:
                            value_list.append(item)
                    user_dict['application'][field.content] = value_list

    user = UserDto.parse_obj(user_dict)
    result: InsertOneResult = await db[Collections.USERS.value].insert_one(document=user_dict)

    webhook_url = settings.discord_applications_webhook_url
    tag = f"<@&{settings.discord_steering_committee_id}>" if is_directorate_app \
        else f"<@{settings.discord_chief_of_staff_id}>"
    print(requests.post(
        url=webhook_url,
        json={
            "content": f":scroll: {tag} New **{'Director' if is_directorate_app else 'Staff'} Application** "
                       f"submitted by {user.first_name} {user.last_name} ({user.email}).\nApplication ID: `{user.id_}`"
                       f"\n\nhttps://api.cimun.org/api/v1/users/export",
            "allowed_mentions": {"parse": ["roles" if is_directorate_app else "users"]}
        }
    ).content)

    if result.inserted_id:
        return user
    else:
        raise HTTPException(400, "Something went wrong, please try again.")


@router.post(
    "/{id_}",
    response_description=f"Create single {collection}",
)
async def post_form(id_: str, request: FormResponsesDto = Body(...)):
    # cast to ObjectId
    form_id = ObjectId(id_)

    # Get original form user filled out
    form: FormDto = FormDto.parse_obj(await db[collection].find_one({"_id": ObjectId(id_)}))
    # Get fields of that form
    fields: List[FormFieldDto] = form.sections[0].fields

    response_map = {}
    for response in request.responses:
        response_map[response.id_] = response.response

    form_responses: FormResponses = FormResponses(form_id=form_id, updated_by="USER_INPUT", created_by="USER_INPUT")

    for field in fields:
        if response_map.get(field.id_):
            form_responses.responses[field.content] = response_map[field.id_]

            if field.field_type == "SELECTION":
                selected_id = ObjectId(response_map[field.id_])

                for value in field.values:
                    if value.id_ == selected_id:
                        form_responses.responses[field.content] = value.value

    result: InsertOneResult = await db[Collections.FORM_RESPONSES.value].insert_one(document=form_responses.dict())

    if result.inserted_id:
        if "Registration" in form.sections[0].title:
            webhook_url = settings.discord_registrations_webhook_url
            tag = f"<@{settings.discord_usg_admin_id}>"

            advisor_name = f"{form_responses.responses['Advisor First Name (Given Name)']} " \
                           f"{form_responses.responses['Advisor Last Name (Surname)']}"
            advisor_email = f"{form_responses.responses['Advisor Email']}"
            school = form_responses.responses['School Name']
            del_count = form_responses.responses['Estimated delegate count']
            print(requests.post(
                url=webhook_url,
                json={
                    "content": f":rotating_light: :school: {tag} **New School Registration** :school: :rotating_light:"
                               f"\n\nSubmitted by {advisor_name} ({advisor_email}) from {school}."
                               f"\nEstimated Delegate Count: {del_count}"
                               f"\n\nApplication ID: `{form_responses.id_}`"
                               f"\n\nhttps://api.cimun.org/api/v1/forms/{form_id}/export",
                    "allowed_mentions": {"parse": ["users"]}
                }
            ).content)

        return 200
    else:
        raise HTTPException(500, "Something went wrong, please try again.")



