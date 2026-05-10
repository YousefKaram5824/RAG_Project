import importlib
from typing import Dict, Any, List

class TemplateParser:

    def __init__(self, language: str = "en"):
        self.language = language
        self._module_cache = {}

    def set_language(self, language: str):
        self.language = language

    def get(self, group: str, key: str, variables: Dict[str, Any] = None):

        module_path = f"stores.llm.template.locales.{self.language}.{group}"
        if module_path in self._module_cache:
            module = self._module_cache[module_path]
        else:
            module = importlib.import_module(module_path)
            self._module_cache[module_path] = module

        if not hasattr(module, key):
            raise ValueError(f"Template key '{key}' not found in {module_path}")

        template = getattr(module, key)

        if variables:
            for k, v in variables.items():
                template = template.replace(f"${k}", str(v))

        return template

    def build_prompt(
        self,
        question: str,
        chunks: List[dict],
        system_template: str,
        footer_template: str
    ):
        prompt_parts = [system_template.strip(), ""]

        for i, chunk in enumerate(chunks, start=1):
            doc_block = self.get(
                "rag", "document_prompt",
                {"doc_id": i, "text": chunk.get("text", "")}
            )
            prompt_parts.append(doc_block.strip())

        prompt_parts.append("")
        prompt_parts.append(footer_template.strip())
        prompt_parts.append("")
        prompt_parts.append(f"Question: {question}")

        return "\n".join(prompt_parts)
