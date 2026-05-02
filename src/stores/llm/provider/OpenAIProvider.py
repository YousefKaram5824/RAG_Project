# =============================================================================
# stores/llm/provider/OpenAIProvider.py — OpenAI-Compatible Text Generation
# =============================================================================
# PURPOSE:
#   Concrete LLM provider for text generation via the OpenAI Chat Completions API.
#   Works with any OpenAI-compatible endpoint:
#     - OpenAI   (https://api.openai.com/v1)
#     - Gemini   (https://generativelanguage.googleapis.com/v1beta/openai)
#     - Ollama   (http://localhost:11434/v1)
#
# IMPLEMENTS: LLMInterface
# CALLED BY:  LLMFactory, NlpController.answer_rag_question()
#
# TEAM NOTE (Ahmed — Phase 3):
#   The OpenAI Python client is already OpenAI-compatible with other providers
#   — just change the base_url and api_key in settings.
#   generate_response() is the key method: it takes the full chat_history
#   built by NlpController and returns the model's text answer.
# =============================================================================

from openai import OpenAI
from stores.llm.LLMInterface import LLMInterface
from typing import List


class OpenAIProvider(LLMInterface):
    """
    Text generation via OpenAI-compatible API.
    """

    def __init__(self):
        self.client = None          # initialized in set_generation_model()
        self.generation_model = None

    def set_generation_model(self, model_name: str):
        """
        Initializes the OpenAI client with the configured base URL and API key.
        Called once at app startup by LLMFactory.

        TODO (Ahmed):
            from helpers.config import get_settings
            settings = get_settings()
            self.client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_API_BASE
            )
            self.generation_model = model_name
        """
        # TODO: implement client initialization
        pass

    def set_embedding_model(self, model_name: str, embedding_size: int):
        """Not used in OpenAIProvider — embeddings are handled by EmbeddingProvider."""
        raise NotImplementedError("OpenAIProvider uses EmbeddingProvider for embeddings.")

    def generate_response(
        self,
        chat_history: List[dict],
        max_tokens: int = 500,
        temperature: float = 0.1
    ) -> str:
        """
        Calls the OpenAI Chat Completions API and returns the text answer.

        Args:
            chat_history: List of {role, content} dicts built by construct_prompt()

        Returns:
            The assistant's reply as a plain string

        TODO (Ahmed):
            response = self.client.chat.completions.create(
                model=self.generation_model,
                messages=chat_history,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        """
        # TODO: implement API call
        pass

    def embed_text(self, text: str, doc_type: str = "passage") -> List[float]:
        """Not used — see EmbeddingProvider for local embeddings."""
        raise NotImplementedError("Use EmbeddingProvider for local embeddings.")

    def construct_prompt(
        self,
        system_prompt: str,
        user_message: str
    ) -> List[dict]:
        """
        Builds the chat message array for the API call.

        Returns:
            [
              {"role": "system", "content": system_prompt},
              {"role": "user",   "content": user_message}
            ]

        TODO (Ahmed):
            return [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message}
            ]
        """
        # TODO: implement prompt construction
        pass

    def process_input_text(self, text: str, max_chars: int) -> str:
        """
        Truncates input text to prevent exceeding the model's context window.

        Args:
            text:      Raw input text
            max_chars: Character limit from settings.MAX_INPUT_TOKENS

        Returns:
            Truncated text string

        TODO (Ahmed):
            return text[:max_chars]
        """
        # TODO: implement truncation
        pass
