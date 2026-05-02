# =============================================================================
# controllers/NlpController.py — Core RAG Logic Controller
# =============================================================================
# PURPOSE:
#   The heart of the entire system. Orchestrates the full RAG pipeline:
#     1. push_data_to_index()    — embed chunks, store vectors in Qdrant
#     2. search_by_vector()      — embed query, retrieve top-k similar chunks
#     3. answer_rag_question()   — retrieve + build prompt + call LLM → answer
#     4. get_project_info()      — check if a Qdrant collection exists
#
# CALLED BY: routes/nlp.py
#
# DEPENDENCIES (injected via constructor — Dependency Injection pattern):
#   - llm_client:     An instance of OpenAIProvider (for text generation)
#   - embed_client:   An instance of EmbeddingProvider (for local embeddings)
#   - vector_db:      An instance of QDrantDB (for vector storage/search)
#   - template_parser: TemplateParser instance (for prompt templates)
#
# TEAM NOTE (Ahmed — Phase 3):
#   This is the most complex file in the project. Build it AFTER all stores
#   (LLMFactory, VectorDBFactory, TemplateParser) are working.
#   Each method below has a clear docstring explaining the exact steps.
# =============================================================================

from typing import List
from controllers.BaseController import BaseController


class NlpController(BaseController):
    """
    Orchestrates the complete RAG pipeline.
    All external dependencies are injected — none are created internally.
    """

    def __init__(self, llm_client, embed_client, vector_db, template_parser):
        """
        Args:
            llm_client:      OpenAIProvider instance (generates text answers)
            embed_client:    EmbeddingProvider instance (converts text → vectors)
            vector_db:       QDrantDB instance (stores and searches vectors)
            template_parser: TemplateParser instance (builds prompts from templates)
        """
        super().__init__()
        self.llm_client = llm_client
        self.embed_client = embed_client
        self.vector_db = vector_db
        self.template_parser = template_parser

    async def push_data_to_index(
        self,
        project_id: str,
        chunks: list,
        do_reset: bool = False
    ) -> dict:
        """
        Embeds all chunks from MongoDB and pushes their vectors to Qdrant.

        Pipeline:
          chunks (from MongoDB) → embed each chunk text → collect vectors
          → create Qdrant collection → batch upsert all vectors

        Args:
            project_id: Used as the Qdrant collection name prefix
            chunks:     List of DataChunk objects from ChunkModel
            do_reset:   If True, delete the existing collection first

        Returns:
            {"message": "Successfully pushed N chunks to index."}

        TODO (Ahmed — Phase 3):
            1. If do_reset → call self.vector_db.delete_collection(project_id)
            2. Create collection: self.vector_db.create_collection(
                   project_id,
                   self.app_settings.EMBEDDING_DIMENSION,
                   self.app_settings.VECTOR_DISTANCE_METRIC
               )
            3. For each chunk in chunks:
                   vector = self.embed_client.embed(chunk.chunk_text, "passage")
            4. Batch upsert: self.vector_db.add_documents(project_id, vectors, chunks)
            5. Return success message with count
        """
        # TODO: implement vector push pipeline
        pass

    async def search_by_vector(
        self,
        project_id: str,
        query_text: str,
        top_k: int = 5
    ) -> list:
        """
        Embeds the query and performs semantic similarity search in Qdrant.

        Pipeline:
          query_text → embed (with "query" prefix) → search Qdrant → return top-k results

        Args:
            project_id: Qdrant collection to search in
            query_text: The user's raw question string
            top_k:      Number of results to retrieve

        Returns:
            List of RetrievalDocument objects [{text, score}, ...]

        TODO (Ahmed — Phase 3):
            1. query_vector = self.embed_client.embed(query_text, "query")
            2. results = self.vector_db.search_by_vector(project_id, query_vector, top_k)
            3. Return results list
        """
        # TODO: implement semantic search
        pass

    async def answer_rag_question(
        self,
        project_id: str,
        question: str,
        top_k: int = 5,
        language: str = "en"
    ) -> dict:
        """
        Full RAG pipeline: retrieve relevant chunks, build a grounded prompt,
        call the LLM, and return the generated answer.

        Pipeline:
          question
            → search_by_vector()        (retrieve top-k relevant chunks)
            → TemplateParser.get()      (load system + document + footer prompts)
            → build_prompt()            (inject chunks into prompt template)
            → llm_client.generate()     (call OpenAI-compatible API)
            → return answer + metadata

        Args:
            project_id: Project to search in
            question:   User's question
            top_k:      Chunks to retrieve for context
            language:   "en" or "ar" — controls which prompt template is loaded

        Returns:
            {
              "answer":       str,    # LLM-generated answer
              "full_prompt":  str,    # The full prompt sent to the LLM (for debugging)
              "chat_history": list    # Message array [{role, content}, ...]
            }

        TODO (Ahmed — Phase 3):
            1. results = await self.search_by_vector(project_id, question, top_k)
            2. self.template_parser.set_language(language)
            3. system_prompt = self.template_parser.get("rag", "system_prompt")
            4. Build document_block by iterating results and formatting each chunk
               using template_parser.get("rag", "document_prompt", {doc_id, text})
            5. footer = self.template_parser.get("rag", "footer_template_prompt")
            6. full_prompt = system_prompt + document_block + question + footer
            7. chat_history = self.llm_client.construct_prompt(system_prompt, full_prompt)
            8. answer = self.llm_client.generate_response(chat_history)
            9. Return {answer, full_prompt, chat_history}
        """
        # TODO: implement full RAG answer pipeline
        pass

    async def get_project_info(self, project_id: str) -> bool:
        """
        Checks whether a Qdrant collection exists for this project.
        Called by GET /api/nlp/index/info/{project_id}

        Returns:
            True if collection exists and is ready for querying, False otherwise

        TODO (Ahmed):
            return self.vector_db.collection_exists(project_id)
        """
        # TODO: implement collection existence check
        pass
