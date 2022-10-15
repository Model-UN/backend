import motor.motor_asyncio

from app.settings import settings

motor_client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_url)
db: motor.motor_asyncio.AsyncIOMotorDatabase = motor_client.nexus
