# =============================================================================
# stores/vectordb/VectorDBFactory.py — Vector DB Provider Factory
# =============================================================================
# PURPOSE:
#   Factory Method Pattern for vector database providers.
#   Currently only supports Qdrant, but structured for easy extension.
#
# CALLED BY: main.py at app startup
# TEAM NOTE (Ahmed — Phase 3):
#   Call this from main.py:
#     vector_db = VectorDBFactory.create("qdrant", settings)
# =============================================================================

from helpers.config import Settings
from controllers.BaseController import BaseController


class VectorDBFactory:
    """
    Creates vector database provider instances by name.
    """

    @staticmethod
    def create(provider_type: str, settings: Settings):
        """
        Factory method — returns the appropriate VectorDB provider.

        Args:
            provider_type: One of:
                           "qdrant" → QDrantDB (local or remote)
                           # Future: "faiss", "pinecone", "weaviate"
            settings: App settings for connection config

        Returns:
            An instance implementing VectorDBInterface

        TODO (Ahmed):
            from stores.vectordb.provider.QDrantDB import QDrantDB

            if provider_type == "qdrant":
                base = BaseController()
                db_path = base.get_db_path()
                client = QDrantDB(path=db_path)
                client.connect()
                return client
            else:
                raise ValueError(f"Unknown vector DB provider: '{provider_type}'")
        """
        # TODO: implement factory method
        pass
