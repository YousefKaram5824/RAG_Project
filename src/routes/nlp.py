# =============================================================================
# routes/nlp.py — NLP & RAG Pipeline Endpoints
# =============================================================================
# PURPOSE:
#   Four endpoints covering Steps 3–5 of the RAG pipeline:
#
#   Step 3 — POST /api/nlp/index/push/{project_id}
#     Embeds all MongoDB chunks and uploads vectors to Qdrant.
#
#   Step 4 — POST /api/nlp/index/search/{project_id}
#     Embeds the query, searches Qdrant, returns top-k similar chunks.
#
#   Step 5 — POST /api/nlp/index/answer/{project_id}
#     Full RAG: retrieve chunks → build prompt → LLM → answer.
#
#   Info  — GET  /api/nlp/index/info/{project_id}
#     Checks whether a Qdrant collection exists for this project.
#
# TEAM NOTE (Pair B — Member 4):
#   NlpController is injected via app.state (set during startup in main.py).
#   Access it with: request.app.state.nlp_controller
#   Do NOT instantiate NlpController directly inside these routes.
# =============================================================================

from fastapi import APIRouter, Request, HTTPException
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from controllers.NlpController import NlpController
from routes.schema.nlp import PushDataRequest, SearchRequest

nlp_router = APIRouter(prefix="/api/nlp", tags=["nlp"])


@nlp_router.post("/index/push/{project_id}")
async def push_to_index(
    project_id: str,
    request_body: PushDataRequest,
    request: Request
):
    """
    Step 3: Embeds chunks from MongoDB and stores vectors in Qdrant.

    Args (path): project_id — MongoDB _id of the project
    Args (body): {"do_reset": 0}

    Returns:
        {"message": "Successfully pushed N chunks to index."}

    Flow:
        1. Verify project exists in MongoDB
        2. Fetch all chunks from ChunkModel (paginated)
        3. Call nlp_controller.push_data_to_index(project_id, chunks, do_reset)

    TODO (Pair B):
        Implement using request.app.state.nlp_controller for the controller.
        Use ChunkModel().get_chunks_by_project_id() with pagination loop.
    """
    # TODO: implement push endpoint body
    pass


@nlp_router.post("/index/search/{project_id}")
async def semantic_search(
    project_id: str,
    request_body: SearchRequest,
    request: Request
):
    """
    Step 4: Semantic similarity search — no LLM involved.

    Returns the raw top-k chunks most similar to the query.
    Useful for debugging retrieval quality before running full RAG.

    Args (body): {"text": "What is X?", "top_k": 5}

    Returns:
        {"results": [{"text": "...", "score": 0.92}, ...]}

    TODO (Pair B):
        Call request.app.state.nlp_controller.search_by_vector(...)
    """
    # TODO: implement search endpoint body
    pass


@nlp_router.post("/index/answer/{project_id}")
async def rag_answer(
    project_id: str,
    request_body: SearchRequest,
    request: Request
):
    """
    Step 5: Full RAG — retrieve, augment, generate.

    Returns an LLM-generated answer grounded in the retrieved document chunks.

    Args (body): {"text": "Explain X", "top_k": 5, "language": "en"}

    Returns:
        {
          "answer":       "The MESI protocol is...",
          "full_prompt":  "## Document No: 1\n...",
          "chat_history": [{"role": "system", "content": "..."}]
        }

    TODO (Pair B):
        Call request.app.state.nlp_controller.answer_rag_question(...)
    """
    # TODO: implement RAG answer endpoint body
    pass


@nlp_router.get("/index/info/{project_id}")
async def get_index_info(project_id: str, request: Request):
    """
    Checks whether a Qdrant vector collection exists for this project.

    Returns:
        {"results": true}   if the collection is ready
        {"results": false}  if the project has not been pushed yet

    TODO (Pair B):
        Call request.app.state.nlp_controller.get_project_info(project_id)
    """
    # TODO: implement info endpoint body
    pass
