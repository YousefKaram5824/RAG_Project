from enum import Enum

class VectorDBProvider(Enum):
    QDRANT = "qdrant"

class DistanceMetric(Enum):
    COSINE = "Cosine"
    DOT = "Dot"

class VectorDBConstants:
    COLLECTION_PREFIX = "collection_"
