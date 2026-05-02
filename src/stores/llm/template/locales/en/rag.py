# =============================================================================
# stores/llm/template/locales/en/rag.py — English Prompt Templates
# =============================================================================
# PURPOSE:
#   Contains the three prompt templates used to build the full RAG prompt
#   that is sent to the LLM. All templates are plain Python string constants.
#
# USED BY: TemplateParser.get("rag", <key>)
#
# CUSTOMISATION (any team member):
#   Edit these strings to change how the LLM behaves, how documents are
#   formatted in the prompt, or what the closing instruction says.
#   Avoid removing the $doc_id and $text placeholders — they are substituted
#   dynamically by TemplateParser.get().
# =============================================================================

# The LLM's persona and core instruction.
# Injected as the system message in the chat history.
system_prompt = """You are a precise and helpful document assistant.
Answer the user's question ONLY using the information provided in the documents below.
If the answer is not found in the documents, say: "I could not find this information in the provided documents."
Do not use your training knowledge — rely solely on the document context.
"""

# Template for formatting one retrieved chunk inside the prompt.
# $doc_id  → sequential number (1, 2, 3, ...)
# $text    → the raw chunk text
document_prompt = """
## Document No: $doc_id
### Content:
$text
---
"""

# Closing instruction added after all document blocks.
# Reminds the LLM what the user's question is and how to respond.
footer_template_prompt = """
Based ONLY on the documents above, answer the following question clearly and concisely.
If the documents do not contain sufficient information, explicitly state that.
"""
