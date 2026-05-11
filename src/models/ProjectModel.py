from models.DataBaseModel import DataBaseModel
from models.db_schemes.project import Project
from typing import Optional, List
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException
class ProjectModel(DataBaseModel):

    COLLECTION_NAME = "projects"

    def __init__(self):
        super().__init__()
        self.collection = self.get_collection(self.COLLECTION_NAME)

    async def create_project(self, project_data: dict):
        result = await self.collection.insert_one(project_data)
        project_data["_id"] = result.inserted_id
        return project_data
    
    async def update_project(self, project_id: str, updates: dict):
        await self.collection.update_one(
            {"_id": ObjectId(project_id)},
            {"$set": updates}
        )

    async def get_project(self, project_id: str):
        try:
            Object_id=ObjectId(project_id)
        except InvalidId:
            raise HTTPException(status_code=400,detail="Invalid_project_id_format")
        return await self.collection.find_one({"_id": Object_id})
       
        

    async def get_project_or_create_one(self, project_id: str):
        existing = await self.collection.find_one({"project_id":project_id})
        if existing:
            return existing
        project_data = {
        "project_id": project_id
        }
        return await self.create_project(project_data)

    async def get_all_projects(self) -> List[Project]:
        docs = await self.collection.find({}).to_list(length=None)
        return [Project(**doc) for doc in docs]