# PURPOSE:
#   Implements VectorDBInterface using the qdrant-client library.
#   Handles all Qdrant operations: collection creation, vector upload, search.
#
# QDRANT CONCEPTS:
#   Collection = a named set of vectors (like a SQL table)
#   Point      = one record: an ID + a vector + a payload (metadata dict)
#   Payload    = arbitrary JSON stored alongside each vector
#                In our case: {"text": "chunk content", "metadata": {...}}
#
# STORAGE MODE:
#   We use local file-based storage (path=db_dir) so no separate Qdrant
#   server is required for development. Docker Compose runs Qdrant as a
#   service for production consistency.

import logging
from typing import List

from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
)

from stores.vectordb.VectorDBInterface import VectorDBInterface
from models.db_schemes.data_chunk import RetrievalDocument
from models.enums.VectorDBEnum import DistanceMetric, VectorDBConstants


logger = logging.getLogger(__name__)

_DISTANCE_MAP = {
    DistanceMetric.COSINE: Distance.COSINE,
    DistanceMetric.DOT:    Distance.DOT,
}


class QDrantDB(VectorDBInterface):

    def __init__(self, path: str = None, url: str = None):
        self.path = path
        self.url = url
        self.client: QdrantClient | None = None

    def connect(self):
        if self.path:
            self.client = QdrantClient(path=self.path)
            logger.info("Connected to Qdrant (local path: %s)", self.path)
        elif self.url:
            self.client = QdrantClient(url=self.url)
            logger.info("Connected to Qdrant (remote url: %s)", self.url)
        else:
            raise ValueError(
                "Either path or url must be provided for QDrantDB"
            )

    @staticmethod
    def _collection_name(project_id: str) -> str:
        return f"{VectorDBConstants.COLLECTION_PREFIX}{project_id}"

    def create_collection(
        self,
        collection_name: str,
        embedding_size: int,
        distance_metric: str = DistanceMetric.COSINE.value,
    ):

        if self.collection_exists(collection_name):
            logger.info(
                "Collection '%s' already exists — skipping creation.",
                self._collection_name(collection_name),
            )
            return

        try:
            metric_enum = DistanceMetric(distance_metric)
        except ValueError:
            logger.warning(
                "Unknown distance metric '%s', defaulting to Cosine.",
                distance_metric,
            )
            metric_enum = DistanceMetric.COSINE

        qdrant_distance = _DISTANCE_MAP[metric_enum]
        full_name = self._collection_name(collection_name)

        self.client.create_collection(
            collection_name=full_name,
            vectors_config=VectorParams(
                size=embedding_size,
                distance=qdrant_distance,
            ),
        )
        logger.info(
            "Created Qdrant collection '%s' (dim=%d, dist=%s)",
            full_name, embedding_size, qdrant_distance.name,
        )

    def add_documents(
        self,
        collection_name: str,
        documents: list,
        vectors: List[List[float]],
        metadata: List[dict] = None,
    ):
        full_name = self._collection_name(collection_name)

        points = [
            PointStruct(
                id=i,
                vector=vectors[i],
                payload={
                    "text":     documents[i].chunk_text,
                    "metadata": documents[i].chunk_metadata,
                },
            )
            for i in range(len(documents))
        ]

        self.client.upsert(collection_name=full_name, points=points)
        logger.info(
            "Upserted %d points into collection '%s'",
            len(points), full_name,
        )

    def search_by_vector(
        self,
        collection_name: str,
        query_vector: List[float],
        top_k: int = 5,
    ) -> List[RetrievalDocument]:

        full_name = self._collection_name(collection_name)

        results = self.client.search(
            collection_name=full_name,
            query_vector=query_vector,
            limit=top_k,
        )

        return [
            RetrievalDocument(text=r.payload["text"], score=r.score)
            for r in results
        ]

    def delete_collection(self, collection_name: str):
        full_name = self._collection_name(collection_name)
        self.client.delete_collection(collection_name=full_name)
        logger.info("Deleted Qdrant collection '%s'", full_name)

    def collection_exists(self, collection_name: str) -> bool:
        full_name = self._collection_name(collection_name)
        return self.client.collection_exists(collection_name=full_name)
