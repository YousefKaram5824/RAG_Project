# IMPLEMENTS: GenerationInterface
# CALLED BY:  LLMFactory, NlpController.answer_rag_question()

from openai import OpenAI
from stores.llm.LLMInterface import GenerationInterface


import logging
from typing import List, Optional

class OpenAIProvider(GenerationInterface):
    def __init__(self, api_key: str, api_url: str=None,
                 default_input_max_characters: int=1000,
                 default_generation_max_output_tokens: int=500,
                 default_generation_temperature: float=0.1) -> None:
        
        self.api_key = api_key
        self.api_url = api_url
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model: str | None = None
        self.logger = logging.getLogger(__name__)

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_url if self.api_url else None
        )

    def set_generation_model(self, model_name: str) -> None:
        self.generation_model = model_name
    
    def generate_response(
        self,
        chat_history: List[dict],
        max_tokens: int = None,
        temperature: float = None,
    ) -> Optional[str]:

        if self.client is None:
            self.logger.error("OpenAI client was not set")
            return None

        if self.generation_model is None:
            self.logger.error("Generation model for OpenAI was not set")
            return None

        max_output_tokens = max_tokens if max_tokens is not None else self.default_generation_max_output_tokens
        temp = temperature if temperature is not None else self.default_generation_temperature

        try:
            response = self.client.chat.completions.create(
                model=self.generation_model,
                messages=chat_history,
                max_tokens=max_output_tokens,
                temperature=temp,
            )

            if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
                self.logger.error("Error while generating text with OpenAI")
                return None

            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"API Error during generation: {str(e)}")
            return None

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
