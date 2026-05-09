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
        if do_reset:
            await self.vector_db.delete_collection(collection_name=project_id)
    
        texts = [chunk.chunk_text for chunk in chunks]
    
        embeddings = self.embed_client.generate_embeddings(texts)
    
        points = []
        for i, chunk in enumerate(chunks):
            points.append({
                "id": chunk.id, # This might casue an issue
                "vector": embeddings[i],
                "payload": {
                    "project_id": project_id, 
                    "text": chunk.chunk_text,
                    "metadata": chunk.chunk_metadata  
                }
            })
    
        await self.vector_db.upsert(collection_name=project_id, points=points)
    
        return {"message": f"Successfully pushed {len(chunks)} chunks to index."}


    async def search_by_vector(
        self,
        project_id: str,
        query_text: str,
        top_k: int = 5
    ) -> list:
        
        query_vector = self.embed_client.generate_embeddings([query_text], input_type="query")[0]

    
        raw_results = await self.vector_db.search(
            collection_name=project_id,
            query_vector=query_vector,
            limit=top_k
        )

        formatted_results = []
        for top in raw_results:
            formatted_results.append({
                "text": top.payload.get("text", ""),    
                "score": top.score,                      
                "metadata": top.payload.get("metadata", {}) 
            })

        return formatted_results
        
    async def answer_rag_question(
        self,
        project_id: str,
        question: str,
        top_k: int = 5,
        language: str = "en"
    ) -> dict:

        
            relevant_chunks = await self.search_by_vector(project_id, question, top_k)

        
            system_template = self.template_parser.get("system_prompt", language)
            footer_template = self.template_parser.get("footer_prompt", language)

            
            full_prompt = self.template_parser.build_prompt(
                question=question,
                chunks=relevant_chunks,
                system_template=system_template,
                footer_template=footer_template
            )

            
            messages = [{"role": "user", "content": full_prompt}]
            answer = await self.llm_client.generate(messages)

            return {
                "answer": answer,
                "full_prompt": full_prompt,  
                "chat_history": messages      
            }
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
    # pass

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
