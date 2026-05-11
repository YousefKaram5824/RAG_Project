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
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status,Request
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
from bson import ObjectId
from bson.errors import InvalidId

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


    project_data = {
        "project_name": dir_name,
        "original_filename": file.filename
    }
    try:
        created_project = await project_model.create_project(project_data)
    except Exception as e:
        logger.error(f"MongoDB project creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project"
        )
    if not created_project:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project record"
        )

    project_id = str(created_project["_id"])

    project_dir_path = project_controller.get_project_path(project_id=project_id)
    os.makedirs(project_dir_path,exist_ok=True)

    file_path, file_id = utilities.generate_unique_filepath(
        orig_file_name=file.filename,
        project_id=project_id
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

    await project_model.update_project(project_id, {"stored_filename": file_id})

    return {
        "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
        "project_id":project_id,
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
   
    #1 look up the project
    if not ObjectId.is_valid(project_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid project_id format"
        )
    if request.chunk_size <= 0:
        raise HTTPException(
            status_code=400,
            detail="chunk_size must be greater than 0"
        )

    if request.overlap < 0:
        raise HTTPException(
            status_code=400,
            detail="overlap cannot be negative"
        )
    if request.overlap >= request.chunk_size:
        raise HTTPException(
            status_code=400,
            detail="overlap must be smaller than chunk_size"
        )
    try:
        project=await project_model.get_project(project_id)
    except InvalidId:
        raise HTTPException(
            status_code=400,
            detail="Invalid MongoDB ObjectId"
        )
    except Exception as e:
        logger.error(f"Project lookup failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error while fetching project"
        )
    if not  project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Project not found")
    stored_filename = project.get("stored_filename")
    if request.project_name.strip()!=project.get("original_filename").strip():
        raise HTTPException(
            status_code=500,
            detail="Enter Correct project name"
        ) 

    
    if not stored_filename:
        raise HTTPException(
            status_code=500,
            detail="Stored filename missing in project"
        )

    
    #2 If do reset
    try:
        if request.do_reset==1:
            await chunk_model.delete_chunks_by_project_id(project_id)
    except Exception as e:
        logger.error(f"Chunk reset failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to reset existing chunks"
        )
    try:
        chunks = process_controller.process_files(
            project_id=project_id,
            filename=stored_filename,
            chunk_size=request.chunk_size,
            overlap=request.overlap
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="File not found on disk"
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        logger.error(f"File processing failed: {e}")

        raise HTTPException(
            status_code=500,
            detail="Document processing failed"
        )

    
    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="No chunks were generated from the document"
        )

   
    try:

        inserted_count = await chunk_model.insert_many_chunks(
            chunks=chunks,
            project_id=project_id
        )

    except Exception as e:
        logger.error(f"Chunk insertion failed: {e}")

        raise HTTPException(
            status_code=500,
            detail="Failed to store chunks in MongoDB"
        )

    return {
        "message": "File processed successfully",
        "inserted_chunks": inserted_count
    }
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
    # TODO: implement process endpoint body
    
