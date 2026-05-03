from enum import Enum

class ResponseSignal(Enum):

    SYSTEM_HEALTHY = "system_is_healthy"
    INTERNAL_SERVER_ERROR = "internal_server_error"
    RESOURCE_NOT_FOUND = "resource_not_found"

    FILE_VALIDATED_SUCCESS = "file_validated_successfully"
    FILE_TYPE_NOT_SUPPORTED = "file_type_not_supported"
    FILE_SIZE_EXCEEDED = "file_size_exceeded"
    FILE_UPLOAD_SUCCESS = "file_uploaded_successfully"
    FILE_UPLOAD_FAILED = "file_upload_failed"
    
    PROCESSING_SUCCESS = "document_processed_and_chunked_successfully"
    PROCESSING_FAILED = "document_processing_failed"
    NO_TEXT_EXTRACTED = "no_text_extracted_from_document"
    PROJECT_NOT_FOUND = "project_id_not_found_in_database"

    INDEX_PUSH_SUCCESS = "chunks_successfully_pushed_to_index"
    INDEX_PUSH_FAILED = "failed_to_push_chunks_to_index"
    INDEX_NOT_FOUND = "vector_index_collection_not_found"
    INDEX_SEARCH_SUCCESS = "vector_search_completed_successfully"

    RAG_ANSWER_SUCCESS = "rag_answer_generated_successfully"
    RAG_GENERATION_FAILED = "rag_answer_generation_failed"
    NO_CONTEXT_RETRIEVED = "no_relevant_context_found_for_query"
    LLM_CONNECTION_ERROR = "failed_to_connect_to_llm_provider"