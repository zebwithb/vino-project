import time
import os
import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.models import QueryRequest, QueryResponse, UploadResponse, FileListResponse, HealthResponse
from app.services.chat_service import chat_service
from app.services.vector_db_service import vector_db_service
from app.services.document_service import (
    store_uploaded_file,
    load_single_document
)
from app import config

# Function to ensure required directories exist
def create_required_directories():
    """
    Ensure all required directories exist.
    """
    os.makedirs(config.USER_UPLOADS_DIR, exist_ok=True)
    os.makedirs(config.DOCUMENTS_DIR, exist_ok=True)
    print(f"Ensured directories: {config.USER_UPLOADS_DIR}, {config.DOCUMENTS_DIR}")

create_required_directories()

# Main FastAPI application setup
app = FastAPI(
    title="Vino AI API",
    description="API for Vino AI project planning assistant and document analysis.",
    version="0.1.0"
)
start_time = time.time()

# CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints ---

@app.post("/v1/chat", response_model=QueryResponse)
async def chat_with_vino(request: QueryRequest, session_id: Optional[str] = Form(None)):
    """
    Main endpoint for interacting with the VINO AI assistant.
    Manages conversation state using a session_id.
    """
    if not session_id:
        session_id = str(uuid.uuid4())  # Generate a new session ID if not provided

    try:
        response_text, updated_history, new_step, new_planner = chat_service.process_query(
            session_id=session_id,
            query_text=request.query_text,
            api_history_data=request.history,
            current_step_override=request.current_step  # Allow client to suggest step
        )
        return QueryResponse(
            response=response_text,
            current_step=new_step,
            planner_details=new_planner
        )
    except Exception as e:
        print(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/v1/upload_document", response_model=UploadResponse)
async def upload_user_document(file: UploadFile = File(...)):
    """
    Uploads a user document, processes it, and adds it to the user's vector collection.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    contents = await file.read()
    stored_path, message = store_uploaded_file(contents, file.filename)

    if not stored_path:
        raise HTTPException(status_code=500, detail=message)

    processing_result, proc_message = load_single_document(stored_path)

    if not processing_result or getattr(processing_result, "chunk_count", 0) == 0:
        raise HTTPException(status_code=400, detail=proc_message or "Failed to process document content.")

    added = vector_db_service.add_documents(
        collection_name=config.USER_DOCUMENTS_COLLECTION_NAME,
        processing_result=processing_result
    )

    if not added:
        raise HTTPException(status_code=500, detail="Document processed but failed to add to vector database.")

    return UploadResponse(
        message=f"'{file.filename}' uploaded and processed successfully. {processing_result.chunk_count} chunks added.",
        filename=file.filename,
        chunks_added=processing_result.chunk_count
    )

@app.get("/v1/list_user_documents", response_model=FileListResponse)
async def list_user_documents():
    """
    Lists documents uploaded by the user and their status in the vector database.
    """
    # Files and chunk counts from the vector database metadata
    db_file_summary = vector_db_service.get_user_document_summary()
    
    if not db_file_summary:
        return FileListResponse(files=[])
        
    # Convert dicts to FileInfo objects
    files = [FileListResponse.__annotations__['files'].__args__[0](**file_dict) for file_dict in db_file_summary]
    return FileListResponse(files=files)

@app.get("/health", response_model=HealthResponse)
async def health():
    """Basic health check endpoint."""
    return HealthResponse(
        status="ok",
        uptime=time.time() - start_time
    )
    