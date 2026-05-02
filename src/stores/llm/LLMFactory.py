# =============================================================================
# stores/llm/LLMFactory.py — LLM Provider Factory (Bonus +5%)
# =============================================================================
# PURPOSE:
#   Implements the Factory Method Pattern for LLM providers.
#   main.py calls this factory at startup to get the correct provider
#   instance without knowing which concrete class it is.
#
# PATTERN: Factory Method
#   The factory reads a provider type string from config (or parameter)
#   and returns the right provider instance. Adding a new provider only
#   requires adding an elif branch here — nothing else in the app changes.
#
# BONUS (+5%):
#   This factory is the implementation of the "LLM Factory Pattern" bonus.
#   Document it in the Tech Report: explain how it enables switching between
#   OpenAI, Gemini, and Ollama with a single config key change.
#
# TEAM NOTE (Ahmed — Phase 3):
#   Call this from main.py startup:
#     llm = LLMFactory.create("openai", settings)
#     embed = LLMFactory.create("local_bge", settings)
# =============================================================================

from helpers.config import Settings


class LLMFactory:
    """
    Creates LLM provider instances by name.
    Decouples the rest of the app from knowing which concrete class to use.
    """

    @staticmethod
    def create(provider_type: str, settings: Settings):
        """
        Factory method — returns the appropriate LLM provider instance.

        Args:
            provider_type: One of:
                           "openai"    → OpenAIProvider (remote API, for text generation)
                           "local_bge" → EmbeddingProvider (local model, for embeddings)
                           # Future providers — add them here:
                           # "gemini"  → GeminiProvider
                           # "ollama"  → OllamaProvider
            settings: App settings (passed to the provider constructor)

        Returns:
            An instance that implements LLMInterface

        Raises:
            ValueError if an unknown provider_type is given

        TODO (Ahmed — Phase 3):
            from stores.llm.provider.OpenAIProvider import OpenAIProvider
            from stores.llm.provider.EmbeddingProvider import EmbeddingProvider

            if provider_type == "openai":
                provider = OpenAIProvider()
                provider.set_generation_model(settings.GENERATE_RESPONSE_MODEL)
                return provider

            elif provider_type == "local_bge":
                provider = EmbeddingProvider()
                provider.set_embedding_model(
                    settings.EMBEDDINGS_MODEL,
                    settings.EMBEDDING_DIMENSION
                )
                return provider

            else:
                raise ValueError(f"Unknown LLM provider: '{provider_type}'")
        """
        # TODO: implement factory method
        pass
