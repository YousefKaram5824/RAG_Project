# =============================================================================
# routes/data.py — Data Upload & Processing Endpoints
# =============================================================================
# PURPOSE:
#   Two endpoints that form the first two steps of the RAG pipeline:
#
#   Step 1 — POST /api/data/upload/{dir_name}
#     Validates and saves an uploaded document to disk,
#     and creates a project record in MongoDB.
#
#   Step 2 — POST /api/data/process/{project_id}
#     Loads the saved file, splits it into chunks,
#     and batch-inserts the chunks into MongoDB.
#
# TEAM NOTE (Pair B — Member 4, routes wiring):
#   This file wires together Pair A's controllers and models.
#   DO NOT put business logic here — only call controllers and return responses.
#   All validation, file loading, and chunking logic lives in the controllers.
# =============================================================================

import aiofiles
import os
import logging
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from helpers.config import Settings, get_settings
from controllers.DataController import DataController
from controllers.FileController import FileController
from controllers.ProcessController import ProcessController
from controllers.ProjectController import ProjectController
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from routes.schema.data import RequestProcess
from models import ResponseSignal
from helpers import utilities

logger = logging.getLogger('uvicorn.error')
data_router = APIRouter(prefix="/api/data", tags=["data"])


@data_router.post("/upload/{dir_name}")
async def upload_file(
    dir_name: str,
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings)
):
    """
    Flow:
        1. Validate file MIME type and size via DataController ✅
        2. Get/create the project in MongoDB via ProjectModel
        3. Resolve the save path via FileController
        4. Stream-write the file to disk using aiofiles
        5. Return success with the project's MongoDB _id

    TODO (Pair B + Pair A):
        Implement the body below by calling the appropriate controllers.
        Use aiofiles.open(file_path, "wb") and await file.read() in chunks.
    """
    # TODO: implement upload endpoint body
    data_controller = DataController()
    project_controller = ProjectController()

    is_valid, signal = data_controller.validate_file(file)
    if not is_valid:
        if signal == ResponseSignal.FILE_TYPE_NOT_SUPPORTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type '{file.content_type}' is not allowed. Accepted types: {settings.FILE_ALLOWED_EXTENSIONS}"
            )
        elif signal == ResponseSignal.FILE_SIZE_EXCEEDED:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds the maximum allowed size of {settings.FILE_MAX_SIZE_MB} MB."
            )

    project_dir_path = project_controller.get_project_path(project_id=dir_name)
    file_path, file_id = utilities.generate_unique_filepath(
        orig_file_name=file.filename,
        project_id=dir_name
    )

    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(settings.FILE_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error while uploading file: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )
    project_model = ProjectModel()
    await project_model.get_project_or_create_one(project_id=dir_name)
    return {
        "signal": ResponseSignal.PROCESSING_SUCCESS.value,
        "message": "File uploaded successfully",
        "file_id": file_id
    }


@data_router.post("/process/{project_id}")
async def process_file(
    project_id: str,
    request: RequestProcess,
    settings: Settings = Depends(get_settings)
):
    """
    Step 2: Loads the uploaded file, chunks it, and stores chunks in MongoDB.

    Args (path):
        project_id: The MongoDB _id of the project (returned by upload)
    Args (body):
        RequestProcess: {project_id (filename), chunk_size, overlap, do_reset}

    Returns:
        int — number of chunks created and inserted into MongoDB

    Flow:
        1. Look up the project in MongoDB (return 404 if not found)
        2. If do_reset=1, delete existing chunks via ChunkModel
        3. Process the file via ProcessController.process_files()
        4. Insert all chunks via ChunkModel.insert_many_chunks()
        5. Return the chunk count

    TODO (Pair B + Pair A):
        Implement the body. Remember project_id in the URL is the MongoDB _id,
        but request.project_id is the filename inside the project folder.
    """
    # TODO: implement process endpoint body'
    
     # 1. Look up project in MongoDB
    project_model = ProjectModel()
    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # 2. If do_reset=1, delete existing chunks
    chunk_model = ChunkModel()

    if request.do_reset == 1:
        await chunk_model.delete_chunks_by_project_id(project_id=project_id)

    # 3. Process the file → get chunks list
    process_controller = ProcessController()

    try:
        chunks = process_controller.process_files(
            project_id=project_id,
            filename=request.project_id,   # ← الفايل نيم جاي من body
            chunk_size=request.chunk_size,
            overlap=request.overlap
        )
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process file: {str(e)}"
        )

    # 4. Insert chunks into MongoDB
    if chunks:
        await chunk_model.insert_many_chunks(
            project_id=project_id,
            chunks=chunks
        )

    # 5. Return chunk count
    return {
        "signal": ResponseSignal.PROCESSING_SUCCESS.value,
        "inserted_chunks": len(chunks)
    }

@data_router.get("/chunks/{project_id}")
async def get_chunks(project_id: str):
    chunk_model = ChunkModel()
    chunks = await chunk_model.get_chunks_by_project_id(project_id=project_id)
    return {
        "project_id": project_id,
        "chunks_count": len(chunks),
        "chunks": [
            {
                "order": c.chunk_order,
                "text": c.chunk_text
            }
            for c in chunks
        ]
    }