from typing import List
from controllers.BaseController import BaseController


class NlpController(BaseController):
    
    def __init__(self, llm_client, embed_client, vector_db, template_parser):
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

        # Create collection (idempotent — skips if exists)
        self.vector_db.create_collection(
            collection_name=project_id,
            embedding_size=self.app_settings.EMBEDDING_DIMENSION,
            distance_metric=self.app_settings.VECTOR_DISTANCE_METRIC,
        )

        # Embed each chunk text
        vectors = []
        for chunk in chunks:
            vector = self.embed_client.embed_text(chunk.chunk_text, doc_type="passage")
            vectors.append(vector)

        # Upsert into Qdrant
        self.vector_db.add_documents(
            collection_name=project_id,
            documents=chunks,
            vectors=vectors,
        )

        return {"message": f"Successfully pushed {len(chunks)} chunks to index."}

    async def search_by_vector(
        self,
        project_id: str,
        query_text: str,
        top_k: int = 5
    ) -> list:
        query_vector = self.embed_client.embed_text(query_text, doc_type="query")

        results = self.vector_db.search_by_vector(
            collection_name=project_id,
            query_vector=query_vector,
            top_k=top_k,
        )

        formatted_results = []
        for r in results:
            formatted_results.append({
                "text": r.text,
                "score": r.score,
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

        self.template_parser.set_language(language)
        system_template = self.template_parser.get("rag", "system_prompt")
        footer_template = self.template_parser.get("rag", "footer_template_prompt")

        full_prompt = self.template_parser.build_prompt(
            question=question,
            chunks=relevant_chunks,
            system_template=system_template,
            footer_template=footer_template,
        )

        chat_history = self.llm_client.construct_prompt(
            system_prompt=system_template,
            user_message=full_prompt,
        )
        answer = self.llm_client.generate_response(chat_history)

        return {
            "answer": answer,
            "full_prompt": full_prompt,
            "chat_history": chat_history,
        }

    async def get_project_info(self, project_id: str) -> bool:
        return self.vector_db.collection_exists(project_id)