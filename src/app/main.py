from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
import uuid

from app.schemas.models import QueryRequest, QueryResponse, UploadResponse, FileListResponse
from app.services.chat_service import ChatService
from app.services.vector_db_service import VectorDBService
from app.services.ingestion_service import IngestionService
# TODO: Import these when they are implemented
# from app.services.document_service import (
#     store_uploaded_file,
#     load_single_document
# )
from app.core.config import settings
from app.dependencies import get_chat_service, get_vector_db_service, get_ingestion_service

# Function to ensure required directories exist
def create_required_directories():
    """
    Ensure all required directories exist.
    """
    os.makedirs(settings.USER_UPLOADS_DIR, exist_ok=True)
    os.makedirs(settings.DOCUMENTS_DIR, exist_ok=True)
    print(f"Ensured directories: {settings.USER_UPLOADS_DIR}, {settings.DOCUMENTS_DIR}")

create_required_directories()

# Main FastAPI application setup
app = FastAPI(
    title="Vino AI API",
    description="API for Vino AI project planning assistant and document analysis.",
    version="0.1.0"
)

# CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints ---

@app.post("/v1/chat", response_model=QueryResponse)
async def chat_with_vino(
    request: QueryRequest, 
    session_id: Optional[str] = Form(None),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Main endpoint for interacting with the VINO AI assistant.
    Manages conversation state using a session_id.
    """
    if not session_id:
        session_id = str(uuid.uuid4())

    try:
        response_text, updated_history, new_step, new_planner = chat_service.process_query(
            session_id=session_id,
            query_text=request.query_text,
            api_history_data=request.history,
            current_step_override=request.current_step
        )
        return QueryResponse(
            response=response_text,
            current_step=new_step,
            planner_details=new_planner
        )
    except Exception as e:
        print(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# TODO: Implement upload document endpoint when store_uploaded_file and load_single_document are available
# @app.post("/v1/upload_document", response_model=UploadResponse)
# async def upload_user_document(
#     file: UploadFile = File(...),
#     vector_db_service: VectorDBService = Depends(get_vector_db_service)
# ):

@app.get("/v1/list_user_documents", response_model=FileListResponse)
async def list_user_documents(
    vector_db_service: VectorDBService = Depends(get_vector_db_service)
):
    """
    Lists documents uploaded by the user and their status in the vector database.
    """
    # TODO: Implement get_user_document_summary method in VectorDBService
    # db_file_summary = vector_db_service.get_user_document_summary()
    
    # For now, return empty list until method is implemented
    return FileListResponse(files=[])


@app.post("/v1/admin/process_directories")
async def process_directories(
    ingestion_service: IngestionService = Depends(get_ingestion_service)
):
    """
    Admin endpoint: Process all documents in the configured directories.
    """
    try:
        result = ingestion_service.process_all_directories()
        return {"status": "success", "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing directories: {str(e)}")


@app.post("/v1/admin/process_single_directory")
async def process_single_directory(
    from_dir: str,
    to_dir: str, 
    source: str = "system_upload",
    ingestion_service: IngestionService = Depends(get_ingestion_service)
):
    """
    Admin endpoint: Process documents from a specific directory.
    """
    try:
        success = ingestion_service.process_directory(from_dir, to_dir, source)
        if success:
            return {"status": "success", "message": f"Successfully processed documents from {from_dir}"}
        else:
            return {"status": "info", "message": f"No documents processed from {from_dir}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing directory: {str(e)}")


@app.get("/v1/collections")
async def list_collections(
    vector_db_service: VectorDBService = Depends(get_vector_db_service)
):
    """
    List all vector database collections and their document counts.
    """
    try:
        collections = vector_db_service.list_collections()
        collection_info = []
        for collection_name in collections:
            count = vector_db_service.get_collection_count(collection_name)
            collection_info.append({
                "name": collection_name,
                "document_count": count
            })
        return {"collections": collection_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing collections: {str(e)}")


@app.get("/health")
async def health_check():
    # Basic health check, can be expanded (e.g., check DB connection)
    return {"status": "healthy", "message": "Vino AI API is running."}

# To run this FastAPI app (save the above as src/app/main.py):
# Ensure you are in the root directory of your project (vino-project)
# Then run: uvicorn src.app.main:app --reload