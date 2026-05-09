from models.DataBaseModel import DataBaseModel
from models.db_schemes.project import Project
from typing import Optional, List

class ProjectModel(DataBaseModel):

    COLLECTION_NAME = "projects"

    def __init__(self):
        super().__init__()
        self.collection = self.get_collection(self.COLLECTION_NAME)

    async def create_project(self, project_id: str) -> Project:
        project = Project(project_id=project_id)
        result = await self.collection.insert_one(project.model_dump(by_alias=True))
        project.id = str(result.inserted_id)
        return project

    async def get_project(self, project_id: str) -> Optional[Project]:
        doc = await self.collection.find_one({"project_id": project_id})
        if not doc:
            return None
        return Project(**doc)

    async def get_project_or_create_one(self, project_id: str) -> Project:
        existing = await self.get_project(project_id)
        if existing:
            return existing
        return await self.create_project(project_id)

    async def get_all_projects(self) -> List[Project]:
        docs = await self.collection.find({}).to_list(length=None)
        return [Project(**doc) for doc in docs]
