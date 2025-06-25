from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

# --- Document Processing Models (Primarily for internal use by services) ---
class FileType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"
    
class DocumentMetadata(BaseModel):
    """Metadata for a document chunk, often used for vector DBs."""
    doc_id: str
    chunk_index: int # Renamed from 'chunk' for clarity
    chunk_length: int # Length of the text chunk
    section: Optional[str] = None 

class DocumentChunk(BaseModel):
    """Represents a processed chunk of a document ready for embedding/storage."""
    metadata: DocumentMetadata
    text: str = Field(..., min_length=1)

class FileMetadata(BaseModel):
    """Information about a single listed file."""
    # Add other relevant info, e.g., size, upload_date, processing_status
    chunks_in_db: Optional[int] = None 
    status: Optional[str] = None
    source: str = Field(..., min_length=1)
    filename: str = Field(..., min_length=1)
    file_size: int = Field(..., ge=0)
    file_type: FileType
    page_count: int
    file_word_count: int
    file_char_count: int
    keywords: List[str]
    abstract: str


class ProcessingResult(BaseModel):
    """
    Results from processing a document, potentially for internal service use
    or a detailed response from a document processing endpoint.
    """
    chunk_all_texts: List[str] = Field(default_factory=list, description="List of text from chunks")
    chunk_ids: List[str] = Field(default_factory=list, description="chunk_ids for ChromaDB")

    doc_metadatas: List[DocumentMetadata] = Field(default_factory=list)
    file_metadatas: List[FileMetadata] = Field(default_factory=list, description="Metadata for ChromaDB")
    chunk_count:  int = Field(default=0, ge=0)
    
    message: Optional[str] = None
    
    @classmethod
    def create_empty(cls) -> 'ProcessingResult':
        """Create an empty ProcessingResult with just the filename."""
        return cls(
            chunk_all_texts=[],
            doc_metadatas=[],
            chunk_ids=[],
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

class FileListResponse(BaseModel):
    """Response model for listing uploaded files."""
    files: List[FileMetadata] # Using a structured FileMetadata model

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


