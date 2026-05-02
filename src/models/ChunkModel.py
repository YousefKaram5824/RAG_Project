# =============================================================================
# models/ChunkModel.py — Chunk CRUD Operations
# =============================================================================
# PURPOSE:
#   All read/write operations for the "chunks" MongoDB collection.
#   After ProcessController splits a document, the chunks land here.
#   NlpController reads them back to embed and push to Qdrant.
#
# COLLECTION: "chunks"
# CALLED BY:
#   routes/data.py  → process endpoint (insert chunks after splitting)
#   routes/nlp.py   → push endpoint (fetch chunks for embedding)
#
# PAGINATION NOTE:
#   Documents can produce thousands of chunks. get_chunks_by_project_id()
#   uses limit/skip pagination so we can embed batches without loading
#   everything into memory at once.
#
# TEAM NOTE (Pair A — both members):
#   insert_many_chunks() must use Motor's insert_many for performance.
#   Single-document inserts in a loop would be very slow on large PDFs.
# =============================================================================

from models.DataBaseModel import DataBaseModel
from models.db_schemes.data_chunk import DataChunk
from typing import List, Optional
from bson import ObjectId


class ChunkModel(DataBaseModel):
    """
    CRUD operations for the MongoDB "chunks" collection.
    """

    COLLECTION_NAME = "chunks"

    def __init__(self):
        super().__init__()
        self.collection = self.get_collection(self.COLLECTION_NAME)

    async def insert_many_chunks(
        self,
        chunks: List[dict],
        project_id: str
    ) -> int:
        """
        Batch-inserts all chunks for a project into MongoDB.

        Args:
            chunks:     List of chunk dicts (from ProcessController.process_files)
            project_id: MongoDB ObjectId string of the parent project

        Returns:
            Number of chunks inserted

        TODO (Pair A):
            1. Add "chunk_project_id" key to each chunk dict
            2. await self.collection.insert_many(chunks)
            3. Return len(chunks)
        """
        # TODO: implement batch insert
        pass

    async def get_chunks_by_project_id(
        self,
        project_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[DataChunk]:
        """
        Paginated fetch of all chunks for a project.
        Called repeatedly by the push endpoint to embed chunks in batches.

        Args:
            project_id: MongoDB ObjectId string of the project
            skip:       Number of documents to skip (for pagination)
            limit:      Max documents to return per page

        Returns:
            List of DataChunk objects

        TODO (Pair A):
            cursor = self.collection.find(
                {"chunk_project_id": project_id}
            ).sort("chunk_order", 1).skip(skip).limit(limit)
            docs = await cursor.to_list(length=limit)
            return [DataChunk(**doc) for doc in docs]
        """
        # TODO: implement paginated fetch
        pass

    async def get_chunk_count(self, project_id: str) -> int:
        """
        Returns the total number of chunks for a project.
        Useful for pagination math in the push endpoint.

        TODO (Pair A):
            return await self.collection.count_documents(
                {"chunk_project_id": project_id}
            )
        """
        # TODO: implement count
        pass

    async def delete_chunks_by_project_id(self, project_id: str) -> int:
        """
        Deletes all chunks for a project.
        Called when do_reset=True is passed to the process endpoint.

        Returns:
            Number of documents deleted

        TODO (Pair A):
            result = await self.collection.delete_many(
                {"chunk_project_id": project_id}
            )
            return result.deleted_count
        """
        # TODO: implement delete
        pass
