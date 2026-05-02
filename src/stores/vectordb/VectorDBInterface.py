# =============================================================================
# stores/vectordb/VectorDBInterface.py — Abstract Vector DB Contract
# =============================================================================
# PURPOSE:
#   Defines the interface that ALL vector database providers must implement.
#   Currently only Qdrant is implemented, but the interface makes it trivial
#   to add FAISS, Pinecone, Weaviate, etc. in the future.
#
# PATTERN: Strategy Pattern (same as LLMInterface)
#   NlpController only depends on VectorDBInterface.
#   Adding a new vector DB requires implementing this interface — nothing else changes.
#
# TEAM NOTE (Ahmed — Phase 3):
#   QDrantDB.py implements this. Review the method signatures carefully before
#   implementing — the parameter names must match exactly.
# =============================================================================

from abc import ABC, abstractmethod
from typing import List


class VectorDBInterface(ABC):
    """
    Abstract contract for all vector database providers.
    """

    @abstractmethod
    def connect(self):
        """Establish connection to the vector database."""
        pass

    @abstractmethod
    def create_collection(
        self,
        collection_name: str,
        embedding_size: int,
        distance_metric: str
    ):
        """
        Creates a new vector collection (table/index) in the database.

        Args:
            collection_name: Unique name, e.g. "collection_demoproject"
            embedding_size:  Number of dimensions in each vector (e.g. 384)
            distance_metric: Similarity metric — "Cosine" or "Dot"
        """
        pass

    @abstractmethod
    def add_documents(
        self,
        collection_name: str,
        documents: list,
        vectors: List[List[float]],
        metadata: List[dict] = None
    ):
        """
        Batch-inserts vectors and their associated text payloads.

        Args:
            collection_name: Target collection
            documents:       List of DataChunk objects (provides text + metadata)
            vectors:         Parallel list of embedding vectors
            metadata:        Optional extra metadata per document
        """
        pass

    @abstractmethod
    def search_by_vector(
        self,
        collection_name: str,
        query_vector: List[float],
        top_k: int = 5
    ) -> list:
        """
        Finds the top-k most similar vectors to the query vector.

        Returns:
            List of RetrievalDocument objects [{text, score}, ...]
        """
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str):
        """Deletes an entire collection and all its vectors."""
        pass

    @abstractmethod
    def collection_exists(self, collection_name: str) -> bool:
        """Returns True if the collection exists, False otherwise."""
        pass
