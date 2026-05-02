# =============================================================================
# stores/llm/provider/EmbeddingProvider.py — Local Sentence-Transformer Embeddings
# =============================================================================
# PURPOSE:
#   Generates text embeddings locally using sentence-transformers.
#   No API key needed — the model runs on your machine.
#
# MODEL: BAAI/bge-small-en (default)
#   - 384-dimensional vectors
#   - Fast inference, good semantic quality
#   - Supports asymmetric retrieval (different prefixes for query vs document)
#
# ASYMMETRIC EMBEDDING (important for RAG quality!):
#   BGE models are trained with asymmetric embeddings:
#     - Documents:  embed with prefix "passage: " → optimised for storage
#     - Queries:    embed with prefix "query: "   → optimised for search
#   Using the wrong prefix hurts retrieval accuracy significantly.
#
# IMPLEMENTS: LLMInterface
# CALLED BY:  LLMFactory, NlpController (for both chunk push and query search)
#
# TEAM NOTE (Ahmed — Phase 3):
#   The model downloads automatically on first use (~130MB for bge-small-en).
#   For Arabic support, consider: paraphrase-multilingual-MiniLM-L12-v2
# =============================================================================

from sentence_transformers import SentenceTransformer
from stores.llm.LLMInterface import LLMInterface
from typing import List


class EmbeddingProvider(LLMInterface):
    """
    Local text embeddings using sentence-transformers (BAAI/bge-small-en).
    """

    def __init__(self):
        self.model = None
        self.embedding_size = None

    def set_generation_model(self, model_name: str):
        """Not used — EmbeddingProvider only does embeddings."""
        raise NotImplementedError("EmbeddingProvider does not support text generation.")

    def set_embedding_model(self, model_name: str, embedding_size: int):
        """
        Loads the sentence-transformer model from HuggingFace (cached locally).
        Called once at app startup by LLMFactory.

        Args:
            model_name:     e.g. "BAAI/bge-small-en"
            embedding_size: Number of dimensions (384 for bge-small-en)

        TODO (Ahmed):
            self.model = SentenceTransformer(model_name)
            self.embedding_size = embedding_size
        """
        # TODO: implement model loading
        pass

    def embed_text(self, text: str, doc_type: str = "passage") -> List[float]:
        """
        Converts a text string to a float vector using the loaded model.

        CRITICAL: Apply the correct prefix based on doc_type:
            doc_type == "passage" → prefix with "passage: "
            doc_type == "query"   → prefix with "query: "

        Args:
            text:     The string to embed
            doc_type: "passage" for document chunks, "query" for search queries

        Returns:
            List of floats (length = self.embedding_size)

        TODO (Ahmed):
            if doc_type == "query":
                text = "query: " + text
            else:
                text = "passage: " + text
            vector = self.model.encode(text)
            return vector.tolist()
        """
        # TODO: implement asymmetric embedding
        pass

    def generate_response(self, chat_history, max_tokens=500, temperature=0.1):
        raise NotImplementedError("EmbeddingProvider does not support text generation.")

    def construct_prompt(self, system_prompt, user_message):
        raise NotImplementedError("EmbeddingProvider does not support prompt construction.")
