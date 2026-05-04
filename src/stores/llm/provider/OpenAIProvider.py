# IMPLEMENTS: GenerationInterface
# CALLED BY:  LLMFactory, NlpController.answer_rag_question()

from openai import OpenAI
from stores.llm.LLMInterface import GenerationInterface
from helpers.config import get_settings
from typing import List

class OpenAIProvider(GenerationInterface):
    def __init__(self) -> None:
        self.client: OpenAI | None = None
        self.generation_model: str | None = None

    def set_generation_model(self, model_name: str) -> None:
        settings = get_settings()
        self.client = OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url=settings.GROQ_API_BASE,
        )
        self.generation_model = model_name

    def generate_response(
        self,
        chat_history: List[dict],
        max_tokens: int = 500,
        temperature: float = 0.1,
    ) -> str:

        if self.client is None:
            raise RuntimeError(
                "OpenAI client not initialised. "
                "Call set_generation_model() first."
            )

        response = self.client.chat.completions.create(
            model=self.generation_model,
            messages=chat_history,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content

    def construct_prompt(
        self,
        system_prompt: str,
        user_message: str,
    ) -> List[dict]:
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ]

    def process_input_text(self, text: str, max_chars: int) -> str:
        return text[:max_chars]
