# =============================================================================
# stores/llm/LLMInterface.py — Abstract LLM Provider Contract
# =============================================================================
# PURPOSE:
#   Defines the interface (abstract base class) that ALL LLM providers must
#   implement. This enforces a consistent API regardless of which provider
#   is active (OpenAI, Gemini, Ollama, etc.).
#
# PATTERN: Strategy Pattern
#   NlpController only knows about LLMInterface — it never imports a
#   concrete provider. Swapping OpenAI for Gemini requires only a config
#   change, not a code change.
#
# USED BY:
#   LLMFactory (creates instances)
#   OpenAIProvider, EmbeddingProvider (implements this contract)
#   NlpController (calls these methods via the interface)
#
# TEAM NOTE (Ahmed — Phase 3):
#   All abstract methods must be implemented by every concrete provider.
#   If a provider doesn't support a method (e.g. EmbeddingProvider can't
#   generate text), it should raise NotImplementedError with a clear message.
# =============================================================================

from abc import ABC, abstractmethod
from typing import List


class LLMInterface(ABC):
    """
    Abstract contract for all LLM providers.
    Every provider (OpenAI, HuggingFace, Ollama, etc.) must implement these methods.
    """

    @abstractmethod
    def set_generation_model(self, model_name: str):
        """Set or switch the text generation model."""
        pass

    @abstractmethod
    def set_embedding_model(self, model_name: str, embedding_size: int):
        """Set or switch the embedding model and declare vector dimensions."""
        pass

    @abstractmethod
    def generate_response(
        self,
        chat_history: List[dict],
        max_tokens: int = 500,
        temperature: float = 0.1
    ) -> str:
        """
        Generate a text response from a list of chat messages.

        Args:
            chat_history: List of {"role": "user"/"system"/"assistant", "content": "..."}
            max_tokens:   Max output tokens
            temperature:  Sampling temperature (0.0 = deterministic)

        Returns:
            The generated text string
        """
        pass

    @abstractmethod
    def embed_text(self, text: str, doc_type: str = "passage") -> List[float]:
        """
        Convert text to a numeric embedding vector.

        Args:
            text:     The string to embed
            doc_type: "passage" for document chunks, "query" for search queries
                      (BGE models use different prefixes for asymmetric retrieval)

        Returns:
            List of floats representing the text as a vector
        """
        pass

    @abstractmethod
    def construct_prompt(
        self,
        system_prompt: str,
        user_message: str
    ) -> List[dict]:
        """
        Builds the chat message array for the LLM API.

        Returns:
            [
              {"role": "system", "content": system_prompt},
              {"role": "user",   "content": user_message}
            ]
        """
        pass
