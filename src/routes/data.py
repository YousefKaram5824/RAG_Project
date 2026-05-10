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
data_router = APIRouter(tags=["data"])


@data_router.post("/upload/{dir_name}")
async def upload_file(
    dir_name: str,
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
    data_controller: DataController = Depends(DataController),
    project_model: ProjectModel = Depends(ProjectModel),
    project_controller: ProjectController = Depends(ProjectController)
):

    # Validate file type and size
    is_valid, signal = data_controller.validate_file(file=file)
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid File"
        )

    # Create or get project in MongoDB
    project = await project_model.get_project_or_create_one(project_id=dir_name)

    project_dir_path = project_controller.get_project_path(project_id=dir_name)
    os.makedirs(project_dir_path, exist_ok=True)

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

        if os.path.exists(file_path):
            os.remove(file_path)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file"
        )
    finally:
        await file.close()

    return {
        "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
        "message": "File uploaded successfully",
        "project_id": dir_name,
        "file_id": file_id
    }


@data_router.post("/process/{project_id}")
async def process_file(
    project_id: str,
    request: RequestProcess,
    settings: Settings = Depends(get_settings),
    project_model: ProjectModel = Depends(ProjectModel),
    chunk_model: ChunkModel = Depends(ChunkModel),
    process_controller: ProcessController = Depends(ProcessController)
):
    # 1. Look up project in MongoDB
    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # 2. If do_reset=1, delete existing chunks
    if request.do_reset == 1:
        await chunk_model.delete_chunks_by_project_id(project_id=project_id)

    # 3. Process the file → get chunks list
    try:
        chunks = process_controller.process_files(
            project_id=project_id,
            filename=request.project_id,   # filename from body
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
async def get_chunks(project_id: str, chunk_model: ChunkModel = Depends(ChunkModel)):
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

