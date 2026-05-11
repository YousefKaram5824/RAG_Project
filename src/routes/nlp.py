from fastapi import APIRouter, Request, HTTPException,status,Depends
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from controllers.NlpController import NlpController
from routes.schema.nlp import PushDataRequest, SearchRequest

nlp_router = APIRouter(tags=["nlp"])

@nlp_router.post("/index/push/{project_id}")
async def push_to_index(
    project_id: str,
    request_body: PushDataRequest,
    request: Request,
    project_model: ProjectModel = Depends(ProjectModel),
    chunk_model: ChunkModel = Depends(ChunkModel)
):
    nlp_controller: NlpController = request.app.state.nlp_controller
    
    project = await project_model.get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    chunks = await chunk_model.get_chunks_by_project_id(project_id)
    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No chunks found for this project."
        )

    response = await nlp_controller.push_data_to_index(
        project_id=project_id,
        chunks=chunks,
        do_reset=request_body.do_reset
    )
    return response

@nlp_router.post("/index/search/{project_id}")
async def semantic_search(
    project_id: str,
    request_body: SearchRequest,
    request: Request
):
    nlp_controller: NlpController = request.app.state.nlp_controller
    results = await nlp_controller.search_by_vector(
        project_id=project_id,
        query_text=request_body.text,
        top_k=request_body.top_k,
        source_file=request_body.source_file,
    )
    return {"results": results}

@nlp_router.post("/index/answer/{project_id}")
async def rag_answer(
    project_id: str,
    request_body: SearchRequest,
    request: Request
):
    nlp_controller: NlpController = request.app.state.nlp_controller
    response_data = await nlp_controller.answer_rag_question(
        project_id=project_id,
        question=request_body.text,
        top_k=request_body.top_k,
        language=request_body.language,
        source_file=request_body.source_file,
    )
    return response_data

@nlp_router.get("/index/info/{project_id}")
async def get_index_info(project_id: str, request: Request):
    nlp_controller: NlpController = request.app.state.nlp_controller
    results = await nlp_controller.get_project_info(project_id)
    return {"results": results}
