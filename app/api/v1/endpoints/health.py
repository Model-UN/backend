from fastapi import APIRouter
from app.db.client import motor_client

router = APIRouter()


@router.get("/")
async def health_check():
    return {"message": "healthy"}


@router.get("/db")
async def mongo_db_health_check():
    db_info = await motor_client.server_info()

    return {"message": bool(db_info)}
