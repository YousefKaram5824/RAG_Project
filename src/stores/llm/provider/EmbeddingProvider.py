# TEAM NOTE:
#   The model downloads automatically on first use (~130MB for bge-small-en).
#   For Arabic support, consider: paraphrase-multilingual-MiniLM-L12-v2

from sentence_transformers import SentenceTransformer
from stores.llm.LLMInterface import EmbeddingInterface
import logging
from typing import List, Optional

class EmbeddingProvider(EmbeddingInterface):

    _PREFIX_MAP = {
        "query":   "query: ",
        "passage": "passage: ",
    }

    def __init__(self) -> None:
        self.model: SentenceTransformer | None = None
        self.embedding_size: int | None = None
        self.logger = logging.getLogger(__name__)

        # TODO: Embedding Cache
        #   self._cache: Dict[str, List[float]] = {}
        #   def _cache_key(self, text: str, doc_type: str) -> str:
        #       return hashlib.md5(f"{doc_type}:{text}".encode()).hexdigest()
        #   Then in embed_text():
        #       key = self._cache_key(text, doc_type)
        #       if key in self._cache:
        #           return self._cache[key]
        #       vector = self.model.encode(prefixed_text).tolist()
        #       self._cache[key] = vector
        #       return vector
        #   Opt: Use functools.lru_cache to cap memory usage.

    def set_embedding_model(self, model_name: str, embedding_size: int) -> None:
        self.model = SentenceTransformer(model_name)
        self.embedding_size = embedding_size

    def embed_text(self, text: str, doc_type: str = "passage"):
        if self.model is None:
            self.logger.error("Embedding model not loaded. Call set_embedding_model() first.")
            return None

        if doc_type not in self._PREFIX_MAP:
            self.logger.error(f"Invalid doc_type '{doc_type}'. Must be one of {list(self._PREFIX_MAP.keys())}.")
            return None

        try:
            prefixed_text = self._PREFIX_MAP[doc_type] + text
            vector = self.model.encode(prefixed_text)
            return vector.tolist()
        except Exception as e:
            self.logger.error(f"Error while embedding text: {str(e)}")
            return None
