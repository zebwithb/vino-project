from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
import uuid # For session IDs

from app.schemas.models import QueryRequest, QueryResponse, UploadResponse, FileListResponse
from app.services.chat_service import chat_service # Singleton instance
from app.services.vector_db_service import vector_db_service # Singleton instance
from app.services.document_service import (
    store_uploaded_file,
    load_single_document
)
from app import config # To access USER_UPLOADS_DIR etc.

# Function to ensure required directories exist
def create_required_directories():
    """
    Ensure all required directories exist.
    """
    os.makedirs(config.USER_UPLOADS_DIR, exist_ok=True)
    os.makedirs(config.DOCUMENTS_DIR, exist_ok=True) # For framework documents
    print(f"Ensured directories: {config.USER_UPLOADS_DIR}, {config.DOCUMENTS_DIR}")

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
    allow_origins=["*"], # Allow all origins for now, restrict in production
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
        session_id = str(uuid.uuid4()) # Generate a new session ID if not provided

    try:
        response_text, updated_history, new_step, new_planner = chat_service.process_query(
            session_id=session_id,
            query_text=request.query_text,
            api_history_data=request.history,
            current_step_override=request.current_step # Allow client to suggest step
        )
        return QueryResponse(
            response=response_text,
            history=updated_history,
            current_step=new_step,
            planner_details=new_planner
            # session_id can be returned if client needs to manage it explicitly
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

    if not processing_result or not processing_result.documents:
        # Clean up stored file if processing failed badly
        # os.remove(stored_path) # Consider if this is desired
        raise HTTPException(status_code=400, detail=proc_message or "Failed to process document content.")

    added = vector_db_service.add_documents(
        collection_name=config.USER_DOCUMENTS_COLLECTION_NAME,
        processing_result=processing_result
    )

    if not added:
        # Clean up stored file if DB add failed
        # os.remove(stored_path) # Consider if this is desired
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
    # Files physically in the upload directory
    # physical_files = list_uploaded_files_in_dir()
    
    # Files and chunk counts from the vector database metadata
    db_file_summary = vector_db_service.get_user_document_summary()
    
    if not db_file_summary:
        return FileListResponse(files=[], message="No user documents found in the database.")
        
    return FileListResponse(files=db_file_summary, message="User documents retrieved successfully.")


@app.get("/health")
async def health_check():
    # Basic health check, can be expanded (e.g., check DB connection)
    return {"status": "healthy", "message": "Vino AI API is running."}

# To run this FastAPI app (save the above as src/app/main.py):
# Ensure you are in the root directory of your project (vino-project)
# Then run: uvicorn src.app.main:app --reload