# =============================================================================
# stores/llm/template/template_parser.py — Prompt Template Engine
# =============================================================================
# PURPOSE:
#   Loads language-specific prompt templates and renders them with dynamic values.
#   Supports English ("en") and Arabic ("ar") out of the box.
#   Adding a new language only requires creating a new locales/<lang>/rag.py file.
#
# HOW IT WORKS:
#   Uses Python's importlib to dynamically import a locale module by language code.
#   The locale module (e.g. locales/en/rag.py) contains string constants
#   for system_prompt, document_prompt, and footer_template_prompt.
#
# CALLED BY: NlpController.answer_rag_question()
#
# TEAM NOTE (Pair B — Member 4):
#   template_parser.get("rag", "document_prompt", {"doc_id": 1, "text": "..."})
#   Uses Python's str.replace() to substitute $doc_id and $text placeholders.
# =============================================================================

import importlib
from typing import Dict, Any


class TemplateParser:
    """
    Dynamically loads and renders locale-specific prompt templates.
    """

    def __init__(self, language: str = "en"):
        self.language = language
        self._module_cache = {}             # cache loaded modules to avoid reimporting

    def set_language(self, language: str):
        """Switch the active language for subsequent get() calls."""
        self.language = language

    def get(self, group: str, key: str, variables: Dict[str, Any] = None) -> str:
        """
        Loads a prompt template by group and key, then substitutes variables.

        Args:
            group:     Template group name — currently always "rag"
            key:       Template key — one of:
                         "system_prompt"          (the LLM's persona/instructions)
                         "document_prompt"        (format for each retrieved chunk)
                         "footer_template_prompt" (closing instructions)
            variables: Dict of substitution values, e.g. {"doc_id": 1, "text": "..."}

        Returns:
            The rendered prompt string with all $variable placeholders replaced.

        TODO (Pair B):
            1. Build module path: f"stores.llm.template.locales.{self.language}.{group}"
            2. importlib.import_module(module_path) to get the locale module
            3. Access getattr(module, key) to get the template string
            4. For each key in variables: template = template.replace(f"${k}", str(v))
            5. Return rendered template

        Example:
            template_parser.get("rag", "document_prompt", {"doc_id": 1, "text": "Cache..."})
            → "## Document No: 1\n### Content: Cache..."
        """
        # TODO: implement template loading and rendering
        pass
