# =============================================================================
# models/DataBaseModel.py — Base Database Model (Parent Class)
# =============================================================================
# PURPOSE:
#   Root class for all MongoDB model classes.
#   Provides a shared Motor async MongoDB client that child models use.
#
# PATTERN: Data Access Object (DAO) base
#   DataBaseModel holds the DB connection.
#   ProjectModel and ChunkModel inherit it and add their own CRUD operations.
#
# MOTOR vs PYMONGO:
#   Motor is the async version of PyMongo. We use Motor because FastAPI is
#   fully async — blocking database calls would freeze the event loop.
#   Motor's API mirrors PyMongo exactly, but all calls are awaited.
#
# TEAM NOTE (Pair A — Phase 0, Day 1):
#   Build alongside BaseController. Both are foundational — nothing works
#   without a working DB connection.
# =============================================================================

import motor.motor_asyncio
from helpers.config import get_settings


class DataBaseModel:
    """
    Base class for all database models. Provides an async MongoDB client.
    """

    def __init__(self):
        self.app_settings = get_settings()

        # Motor client — async, non-blocking
        # Connection is lazy: it doesn't actually connect until the first operation
        client = motor.motor_asyncio.AsyncIOMotorClient(
            self.app_settings.MONGODB_URI
        )

        # Select the database (creates it if it doesn't exist)
        self.db_client = client[self.app_settings.MONGODB_DB_NAME]

    def get_collection(self, collection_name: str):
        """
        Returns a Motor collection handle by name.

        Args:
            collection_name: e.g. "projects" or "chunks"

        Returns:
            AsyncIOMotorCollection object — supports .find(), .insert_one(), etc.

        Usage in child classes:
            col = self.get_collection("projects")
            doc = await col.find_one({"project_id": "test"})
        """
        return self.db_client[collection_name]
