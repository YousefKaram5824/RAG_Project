# =============================================================================
# models/ProjectModel.py — Project CRUD Operations
# =============================================================================
# PURPOSE:
#   All read/write operations for the "projects" MongoDB collection.
#   A "project" is simply a named workspace for uploaded documents.
#
# COLLECTION: "projects"
# CALLED BY:
#   routes/data.py  → upload endpoint (create project if it doesn't exist)
#   routes/nlp.py   → push/search/answer (verify project exists before NLP ops)
#
# PATTERN: Repository
#   All MongoDB queries for "projects" are in this one class.
#   Routes never query MongoDB directly — they always go through this model.
#
# TEAM NOTE (Pair A — Member 2):
#   get_project_or_create_one() is called from the upload endpoint.
#   It's safe to call it multiple times — it's idempotent (won't create duplicates).
# =============================================================================

from models.DataBaseModel import DataBaseModel
from models.db_schemes.project import Project
from typing import Optional, List


class ProjectModel(DataBaseModel):
    """
    CRUD operations for the MongoDB "projects" collection.
    """

    COLLECTION_NAME = "projects"

    def __init__(self):
        super().__init__()
        self.collection = self.get_collection(self.COLLECTION_NAME)

    async def create_project(self, project_id: str) -> Project:
        """
        Creates a new project document in MongoDB.

        Args:
            project_id: Alphanumeric project name (validated by Project schema)

        Returns:
            The newly created Project object

        TODO (Pair A):
            1. project = Project(project_id=project_id)
            2. result  = await self.collection.insert_one(project.dict(by_alias=True))
            3. Set project.id = str(result.inserted_id)
            4. Return project
        """
        # TODO: implement create
        pass

    async def get_project(self, project_id: str) -> Optional[Project]:
        """
        Finds a project by its project_id string.

        Returns:
            Project object if found, None otherwise

        TODO (Pair A):
            doc = await self.collection.find_one({"project_id": project_id})
            if not doc: return None
            return Project(**doc)
        """
        # TODO: implement find one
        pass

    async def get_project_or_create_one(self, project_id: str) -> Project:
        """
        Idempotent upsert: returns existing project or creates a new one.
        This is the primary method called from the upload route.

        TODO (Pair A):
            existing = await self.get_project(project_id)
            if existing: return existing
            return await self.create_project(project_id)
        """
        # TODO: implement upsert
        pass

    async def get_all_projects(self) -> List[Project]:
        """
        Returns all projects in the collection (useful for admin/debug).

        TODO (Pair A):
            docs = await self.collection.find({}).to_list(length=None)
            return [Project(**doc) for doc in docs]
        """
        # TODO: implement list all
        pass
