from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# --- Document Processing Models (Primarily for internal use by services) ---
class DocumentMetadata(BaseModel):
    """Metadata for a document chunk, often used for vector DBs."""
    source: str  # e.g., path or URL of the original document
    filename: str # Original filename
    chunk_index: int # Renamed from 'chunk' for clarity
    # Add other relevant metadata like page_number, etc.

class DocumentChunk(BaseModel):
    """Represents a processed chunk of a document ready for embedding/storage."""
    id: str # Unique ID for the chunk
    text: str # The actual text content of the chunk
    metadata: DocumentMetadata # Associated metadata

class ProcessingResult(BaseModel):
    """
    Results from processing a document, potentially for internal service use
    or a detailed response from a document processing endpoint.
    """
    
    filename: str
    documents_processed_texts: List[str] = Field(default_factory=list, description="List of text from chunks")
    metadatas_for_db: List[Dict[str, Any]] = Field(default_factory=list, description="Metadata for ChromaDB")
    ids_for_db: List[str] = Field(default_factory=list, description="IDs for ChromaDB")
    chunk_count: int = 0
    message: Optional[str] = None
    
    @classmethod
    def create_empty(cls, filename: str) -> 'ProcessingResult':
        """Create an empty ProcessingResult with just the filename."""
        return cls(
            filename=filename,
            documents_processed_texts=[],
            metadatas_for_db=[],
            ids_for_db=[],
            chunk_count=0
        )


# --- API Request/Response Models ---

class QueryRequest(BaseModel): # This is your primary ChatRequest
    """Request model for the main chat/query endpoint."""
    session_id: str # Added: Crucial for ChatService
    query_text: str
    history: List[Dict[str, Any]] = Field(default_factory=list)
    current_step: Optional[int] = 1 # Made Optional to align with ChatService override
    planner_details: Optional[str] = None
    
    # New fields from Reflex frontend payload
    selected_alignment: Optional[str] = None
    explain_active: Optional[bool] = False
    tasks_active: Optional[bool] = False
    uploaded_file_context_name: Optional[str] = None

class QueryResponse(BaseModel): # This is your primary ChatResponse
    """Response model for the main chat/query endpoint."""
    response: str
    current_step: int
    # History is usually managed by the client (Reflex) and ChatService state,
    # so not typically returned in each response unless specifically needed.
    # history: List[Dict[str, Any]] 
    planner_details: Optional[str] = None # Or Dict[str, Any] if structured

class UploadResponse(BaseModel): # For file upload operations
    """Response model for file upload operations."""
    message: str # General status message (e.g., "File uploaded successfully")
    filename: str # The name of the uploaded file
    detail: Optional[str] = None # More specific detail, e.g. from processing
    chunks_added: Optional[int] = 0 # If applicable and known at upload time

class FileInfo(BaseModel):
    """Information about a single listed file."""
    filename: str
    # Add other relevant info, e.g., size, upload_date, processing_status
    chunks_in_db: Optional[int] = None 
    status: Optional[str] = None

class FileListResponse(BaseModel):
    """Response model for listing uploaded files."""
    files: List[FileInfo] # Using a structured FileInfo model

class HealthResponse(BaseModel):
    status: str
    uptime: float

    class Config:
        schema_extra = {
            "example": {
                "status": "ok",
                "uptime": 123.45
            }
        }


