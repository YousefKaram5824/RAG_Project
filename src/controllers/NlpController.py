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
            self.vector_db.delete_collection(collection_name=project_id)
        if not self.vector_db.collection_exists(project_id):

            self.vector_db.create_collection(
                collection_name=project_id,
                embedding_size=self.embed_client.embedding_size
            )
    
        texts = [chunk.chunk_text for chunk in chunks]
    
        embeddings = [
            self.embed_client.embed_text(text)
            for text in texts
        ]
    
        valid_documents = []
        valid_vectors = []
        for chunk,embedding in zip(chunks,embeddings):
            if embedding is None:
                continue
            valid_documents.append(chunk)
            valid_vectors.append(embedding)
        
        self.vector_db.add_documents(collection_name=project_id, documents=valid_documents,vectors=valid_vectors)
        
        return {"message": f"Successfully pushed {len(chunks)} chunks to index."}


    async def search_by_vector(
        self,
        project_id: str,
        query_text: str,
        top_k: int = 5
    ) -> list:
        
        query_vector = self.embed_client.embed_text(text=query_text, doc_type="query")

        if query_vector is None:
            return []

        raw_results =  self.vector_db.search_by_vector(
            collection_name=project_id,
            query_vector=query_vector,
            top_k=top_k
        )
        #MIN_SCORE = 0.84
        formatted_results = []
        for top in raw_results:
            #if top.score<MIN_SCORE:
                #continue
            formatted_results.append({
                "text": top.text,    
                "score": top.score,                     
            })

        return formatted_results
        
    async def answer_rag_question(
        self,
        project_id: str,
        question: str,
        top_k: int = 5,
        language: str = "en"
    ) -> dict:

        
        relevant_chunks = await self.search_by_vector(project_id=project_id,query_text=question, top_k=top_k)

        self.template_parser.set_language(language)
        system_template = self.template_parser.get("rag", "system_prompt")
        doc_blocks=[]
        for i,chunk in enumerate(relevant_chunks):
            doc_blocks.append( self.template_parser.get("rag", "document_prompt",{"doc_id":i+1,"text": str(chunk)}))
        footer_template = self.template_parser.get("rag", "footer_template_prompt")

        
        full_prompt = (
            system_template
            + "\n".join(doc_blocks)
            + footer_template
            + f"\n\nQuestion: {question}"
        )

        
        messages = [
            {"role": "system", "content": system_template},
            {"role": "user", "content": full_prompt}
        ]
        answer =  self.llm_client.generate_response(messages)

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

    async def get_project_info(self, project_id: str) -> dict:

        collection_name = self.vector_db._collection_name(project_id)
        exists= self.vector_db.collection_exists(project_id)

        if not exists:
            return {
                "indexed": False,
                "chunks": 0,
                "Collection":collection_name,
                "massage": "project not pushed yet"
            }
        
        info = self.vector_db.client.get_collection(collection_name)
        return {
            "indexed": True,
            "Chunks":info.points_count,
            "vectors_config":str(info.config.params.vectors) if info.config else None,
            "Collection": collection_name
        }
        """
        Checks whether a Qdrant collection exists for this project.
        Called by GET /api/nlp/index/info/{project_id}

        Returns:
            True if collection exists and is ready for querying, False otherwise

        TODO (Ahmed):
            return self.vector_db.collection_exists(project_id)
        """
        # TODO: implement collection existence check