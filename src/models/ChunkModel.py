from models.DataBaseModel import DataBaseModel
from models.db_schemes.data_chunk import DataChunk
from typing import List, Optional
from bson import ObjectId

class ChunkModel(DataBaseModel):

    COLLECTION_NAME = "chunks"

    def __init__(self):
        super().__init__()
        self.collection = self.get_collection(self.COLLECTION_NAME)

    async def insert_many_chunks(
        self,
        chunks: List[dict],
        project_id: str
    ):
        for chunk in chunks:
            chunk["chunk_project_id"] = project_id
        await self.collection.insert_many(chunks)
        return len(chunks)

    async def get_chunks_by_project_id(
        self,
        project_id: str,
        skip: int = 0,
        limit: int = 50
    ):
        cursor = self.collection.find(
            {"chunk_project_id": project_id}
        ).sort("chunk_order", 1).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [DataChunk(**doc) for doc in docs]

    async def get_chunk_count(self, project_id: str):
        return await self.collection.count_documents(
            {"chunk_project_id": project_id}
        )

    async def delete_chunks_by_project_id(self, project_id: str):
        result = await self.collection.delete_many(
            {"chunk_project_id": project_id}
        )
        return result.deleted_count