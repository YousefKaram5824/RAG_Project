from abc import ABC, abstractmethod
from typing import List

class GenerationInterface(ABC):

    @abstractmethod
    def set_generation_model(self, model_name: str) -> None:
        pass

    @abstractmethod
    def generate_response(
        self,
        chat_history: List[dict],
        max_tokens: int = 500,
        temperature: float = 0.1,
    ) -> str:
        pass

    @abstractmethod
    def construct_prompt(
        self,
        system_prompt: str,
        user_message: str,
    ) -> List[dict]:
        pass


class EmbeddingInterface(ABC):

    @abstractmethod
    def set_embedding_model(self, model_name: str, embedding_size: int) -> None:
        pass

    @abstractmethod
    def embed_text(self, text: str, doc_type: str = "passage") -> List[float]:
        pass
