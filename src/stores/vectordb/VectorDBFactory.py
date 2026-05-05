import logging
from helpers.config import Settings
from controllers.BaseController import BaseController
from models.enums.VectorDBEnum import VectorDBProvider
from stores.vectordb.VectorDBInterface import VectorDBInterface

logger = logging.getLogger(__name__)

class VectorDBFactory:

    @staticmethod
    def create(
        provider_type: VectorDBProvider,
        settings: Settings,
    ) -> VectorDBInterface:
        # lazy imports to avoid circular deps
        if provider_type == VectorDBProvider.QDRANT:
            from stores.vectordb.provider.QDrantDB import QDrantDB

            base = BaseController(app_settings=settings)
            db_path = base.get_db_path()

            client = QDrantDB(path=db_path)
            client.connect()

            logger.info("QDrantDB provider created (local path: %s)", db_path)
            return client

        raise ValueError(
            f"Unknown vector DB provider: '{provider_type}'. "
            f"Available: {[p.value for p in VectorDBProvider]}"
        )
