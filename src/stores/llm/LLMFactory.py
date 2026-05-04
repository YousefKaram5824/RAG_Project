# BONUS (+5%):
#   This factory is the implementation of the "LLM Factory Pattern" bonus.
#   Document it in the Tech Report: explain how it enables switching between
#   OpenAI, Gemini, and Ollama with a single config key change.

from typing import Callable, Dict, Union
from helpers.config import Settings
from stores.llm.LLMInterface import GenerationInterface, EmbeddingInterface
from models.enums.LLMEnum import LLMProvider

class LLMFactory:
    _REGISTRY: Dict[str, Callable] = {}

    @classmethod
    def register(cls, provider_type: str, provider_class: Callable) -> None:
        cls._REGISTRY[provider_type] = provider_class

    @staticmethod
    def create(provider_type: LLMProvider, settings: Settings) -> Union[GenerationInterface, EmbeddingInterface]:

        # lazy imports to avoid circular deps
        if provider_type == LLMProvider.OPENAI:
            from stores.llm.provider.OpenAIProvider import OpenAIProvider

            provider = OpenAIProvider()
            provider.set_generation_model(settings.GENERATE_RESPONSE_MODEL)
            return provider

        elif provider_type == LLMProvider.LOCAL_BGE:
            from stores.llm.provider.EmbeddingProvider import EmbeddingProvider

            provider = EmbeddingProvider()
            provider.set_embedding_model(
                settings.EMBEDDINGS_MODEL,
                settings.EMBEDDING_DIMENSION,
            )
            return provider

        elif provider_type.value in LLMFactory._REGISTRY:
            provider_class = LLMFactory._REGISTRY[provider_type.value]
            provider = provider_class()

            if hasattr(provider, "set_generation_model"):
                try:
                    provider.set_generation_model(
                        settings.GENERATE_RESPONSE_MODEL
                    )
                except NotImplementedError:
                    pass  # provider is embedding-only; skip
            return provider

        else:
            available = [p.value for p in LLMProvider] + list(
                LLMFactory._REGISTRY.keys()
            )
            raise ValueError(
                f"Unknown LLM provider: '{provider_type}'. "
                f"Available providers: {available}"
            )
