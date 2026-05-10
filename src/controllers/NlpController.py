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

        self.template_parser.set_language(language)
        system_template = self.template_parser.get("rag", "system_prompt")
        footer_template = self.template_parser.get("rag", "footer_template_prompt")

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

    async def get_project_info(self, project_id: str) -> bool:
        return self.vector_db.collection_exists(project_id)