# BONUS (+5%):
#   This factory is the implementation of the "LLM Factory Pattern" bonus.
#   Document it in the Tech Report: explain how it enables switching between
#   OpenAI, Gemini, and Ollama with a single config key change.

from typing import Callable, Dict, Union, Optional
import logging
from helpers.config import Settings
from stores.llm.LLMInterface import GenerationInterface, EmbeddingInterface
from models.enums.LLMEnum import LLMProvider

class LLMFactory:
    _REGISTRY: Dict[str, Callable] = {}

    def __init__(self, config: Settings):
        self.config = config
        self.logger = logging.getLogger(__name__)

    @classmethod
    def register(cls, provider_type: str, provider_class: Callable) -> None:
        cls._REGISTRY[provider_type] = provider_class

    def create(self, provider_type: LLMProvider) -> Optional[Union[GenerationInterface, EmbeddingInterface]]:

        # lazy imports to avoid circular deps
        if provider_type == LLMProvider.OPENAI:
            from stores.llm.provider.OpenAIProvider import OpenAIProvider

            provider = OpenAIProvider(
                api_key=self.config.GROQ_API_KEY,
                api_url=self.config.GROQ_API_BASE,
                default_input_max_characters=self.config.MAX_INPUT_TOKENS,
                default_generation_max_output_tokens=self.config.MAX_RESPONSE_TOKENS,
                default_generation_temperature=self.config.TEMPERATURE
            )
            provider.set_generation_model(self.config.GENERATE_RESPONSE_MODEL)
            return provider

        elif provider_type == LLMProvider.LOCAL_BGE:
            from stores.llm.provider.EmbeddingProvider import EmbeddingProvider

            provider = EmbeddingProvider()
            provider.set_embedding_model(
                self.config.EMBEDDINGS_MODEL,
                self.config.EMBEDDING_DIMENSION,
            )
            return provider

        elif provider_type.value in self._REGISTRY:
            provider_class = self._REGISTRY[provider_type.value]
            provider = provider_class(self.config)

            if hasattr(provider, "set_generation_model"):
                try:
                    provider.set_generation_model(
                        self.config.GENERATE_RESPONSE_MODEL
                    )
                except NotImplementedError:
                    pass  # provider is embedding-only; skip
            return provider

        else:
            available = [p.value for p in LLMProvider] + list(
                self._REGISTRY.keys()
            )
            self.logger.error(
                f"Unknown LLM provider: '{provider_type}'. "
                f"Available providers: {available}"
            )
            return None
