import motor.motor_asyncio
from helpers.config import get_settings

class DataBaseModel:

    def __init__(self):
        self.app_settings = get_settings()

        client = motor.motor_asyncio.AsyncIOMotorClient(
            self.app_settings.MONGODB_URI
        )

        self.db_client = client[self.app_settings.MONGODB_DB_NAME]

    def get_collection(self, collection_name: str):
        return self.db_client[collection_name]
