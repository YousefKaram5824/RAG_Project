from enum import Enum

class LLMProvider(Enum):
    OPENAI = "openai"
    LOCAL_BGE = "local_bge"

class DocumentTypeEnum(Enum):
    DOCUMENT = "document"
    QUERY = "query"