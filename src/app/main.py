from fastapi import FastAPI, HTTPException, Depends, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging

from app.schemas.models import FileListResponse
from app.services.chat_service import ChatService
from app.services.vector_db_service import VectorDBService
from app.services.ingestion_service import IngestionService
from app.endpoints.chat import router as chat_router
from app.core.config import settings
from app.dependencies import get_chat_service, get_vector_db_service, get_ingestion_service, get_session_storage_service
from app.core.exceptions import (
    LLMInitializationError,
    LLMInvocationError,
    PromptGenerationError,
    SessionStorageError,
    SupabaseServiceError,
    VinoError
)

# Configure logging
logger = logging.getLogger(__name__)

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
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION
)

# CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router)

# --- Exception Handlers ---

@app.exception_handler(LLMInitializationError)
async def llm_initialization_exception_handler(request: Request, exc: LLMInitializationError):
    logger.error(f"LLM Initialization Error: {exc.message}")
    return JSONResponse(
        status_code=503,
        content={"detail": f"Language model service unavailable: {exc.message}"}
    )

@app.exception_handler(LLMInvocationError)
async def llm_invocation_exception_handler(request: Request, exc: LLMInvocationError):
    logger.error(f"LLM Invocation Error: {exc.message}")
    return JSONResponse(
        status_code=503,
        content={"detail": f"Language model request failed: {exc.message}"}
    )

@app.exception_handler(PromptGenerationError)
async def prompt_generation_exception_handler(request: Request, exc: PromptGenerationError):
    logger.error(f"Prompt Generation Error: {exc.message}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {exc.message}"}
    )

@app.exception_handler(SessionStorageError)
async def session_storage_exception_handler(request: Request, exc: SessionStorageError):
    logger.warning(f"Session Storage Error: {exc.message}")
    return JSONResponse(
        status_code=503,
        content={"detail": f"Session service temporarily unavailable: {exc.message}"}
    )

@app.exception_handler(SupabaseServiceError)
async def supabase_service_exception_handler(request: Request, exc: SupabaseServiceError):
    logger.error(f"Supabase Service Error: {exc.message}")
    return JSONResponse(
        status_code=503,
        content={"detail": f"Database service unavailable: {exc.message}"}
    )

@app.exception_handler(VinoError)
async def vino_exception_handler(request: Request, exc: VinoError):
    logger.error(f"Application Error: {exc.message}")
    return JSONResponse(
        status_code=400,
        content={"detail": f"Application error: {exc.message}"}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected internal server error occurred"}
    )

# --- API Endpoints ---

@app.post("/v1/upload_document")
async def upload_user_document(
    file: UploadFile = File(...),
    ingestion_service: IngestionService = Depends(get_ingestion_service)
):
    """
    Upload a document for processing and storage in the vector database.
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
            
        # Save the uploaded file
        file_path = os.path.join(settings.USER_UPLOADS_DIR, file.filename)
        
        # Write the file to disk
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Use the existing process_directory method to process the uploaded file
        # by processing the user uploads directory
        success = ingestion_service.process_directory(
            from_dir=settings.USER_UPLOADS_DIR,
            to_dir=settings.USER_UPLOADS_DIR,
            source="user_upload"
        )
        
        return {
            "message": "File uploaded and processed successfully" if success else "File uploaded but processing failed",
            "filename": file.filename,
            "detail": "File has been processed and added to vector database" if success else "Processing failed",
            "chunks_added": 1 if success else 0  # Simplified for now
        }
        
    except Exception as e:
        logger.error(f"Error uploading document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

# TODO: Implement when store_uploaded_file and load_single_document are available

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


@app.get("/v1/admin/session/{session_id}")
async def get_session_info(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Admin endpoint: Get information about a specific chat session.
    """
    try:
        session_info = chat_service.get_session_info(session_id)
        if session_info:
            return {"session": session_info}
        else:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving session info: {str(e)}")


@app.delete("/v1/admin/session/{session_id}")
async def delete_session(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Admin endpoint: Delete a specific chat session.
    """
    try:
        success = chat_service.delete_session(session_id)
        if success:
            return {"message": f"Session {session_id} deleted successfully"}
        else:
            return {"message": f"Session {session_id} not found or could not be deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")


@app.post("/v1/admin/cleanup_sessions")
async def cleanup_old_sessions(
    days_old: int = 30,
    session_storage_service = Depends(get_session_storage_service)
):
    """
    Admin endpoint: Clean up sessions older than specified days.
    """
    try:
        deleted_count = session_storage_service.cleanup_old_sessions(days_old)
        return {
            "message": "Cleanup completed",
            "deleted_sessions": deleted_count,
            "days_threshold": days_old
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during cleanup: {str(e)}")


@app.get("/health")
async def health_check():
    # Basic health check, can be expanded (e.g., check DB connection)
    return {"status": "healthy", "message": "Vino AI API is running."}