from abc import ABC, abstractmethod
from typing import List

class VectorDBInterface(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def create_collection(
        self,
        collection_name: str,
        embedding_size: int,
        distance_metric: str
    ):
        pass

    @abstractmethod
    def add_documents(
        self,
        collection_name: str,
        documents: list,
        vectors: List[List[float]],
        metadata: List[dict] = None
    ):
        pass

    @abstractmethod
    def search_by_vector(
        self,
        collection_name: str,
        query_vector: List[float],
        top_k: int = 5
    ) -> list:
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str):
        pass

    @abstractmethod
    def collection_exists(self, collection_name: str) -> bool:
        pass
