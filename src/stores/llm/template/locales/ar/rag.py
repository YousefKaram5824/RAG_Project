# =============================================================================
# stores/llm/template/locales/ar/rag.py — Arabic Prompt Templates (Bonus +10%)
# =============================================================================
# PURPOSE:
#   Arabic versions of the RAG prompt templates.
#   Used when the user passes language="ar" to the answer endpoint.
#
# ARABIC NLP CHALLENGES (document in Tech Report):
#   1. RTL text direction — Arabic reads right to left. The LLM handles
#      this natively; we must ensure the text reaches it correctly encoded.
#   2. Ligatures — Arabic letters connect differently depending on position.
#      arabic-reshaper fixes this for PDF-extracted text.
#   3. Diacritics — short vowels (harakat) may or may not appear.
#      The embedding model handles these implicitly.
#   4. Morphological complexity — one Arabic root can generate dozens of
#      word forms. Semantic embedding models handle this better than BM25.
#
# TEAM NOTE (Pair A — Member 3, Arabic Bonus):
#   Write your Arabic test case query in the evaluation report and explain
#   how the system handled or failed to handle Arabic input.
# =============================================================================

system_prompt = """أنت مساعد وثائق دقيق ومفيد.
أجب على سؤال المستخدم فقط باستخدام المعلومات الواردة في الوثائق أدناه.
إذا لم تجد الإجابة في الوثائق، قل: "لم أتمكن من العثور على هذه المعلومات في الوثائق المقدمة."
لا تستخدم معرفتك التدريبية — اعتمد فقط على سياق الوثيقة.
"""

document_prompt = """
## وثيقة رقم: $doc_id (المصدر: $source)
### المحتوى:
$text
---
"""

footer_template_prompt = """
بناءً فقط على الوثائق أعلاه، أجب على السؤال التالي بوضوح وإيجاز.
إذا كانت الوثائق لا تحتوي على معلومات كافية، صرّح بذلك صراحةً.
"""
