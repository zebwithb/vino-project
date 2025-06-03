from typing import List, Dict, Any
from pydantic import BaseModel, Field

class DocumentMetadata(BaseModel):
    """Metadata for a document chunk."""
    source: str
    filename: str
    chunk: int

class DocumentChunk(BaseModel):
    """A chunk of text with its metadata and ID."""
    text: str
    metadata: DocumentMetadata
    id: str

class ProcessingResult(BaseModel):
    """Results from processing a document."""
    documents: List[str] = Field(default_factory=list)
    metadatas: List[Dict[str, Any]] = Field(default_factory=list) # Storing as dict for ChromaDB
    ids: List[str] = Field(default_factory=list)
    chunk_count: int = 0

# Models for API requests/responses (can be expanded)
class QueryRequest(BaseModel):
    query_text: str
    history: List[Dict[str, Any]] = Field(default_factory=list)
    current_step: int = 1
    planner_details: str | None = None

class QueryResponse(BaseModel):
    response: str
    current_step: int
    history: List[Dict[str, Any]]
    planner_details: str | None = None

class UploadResponse(BaseModel):
    message: str
    filename: str | None = None
    chunks_added: int = 0

class FileListResponse(BaseModel):
    files: List[Dict[str, Any]] # e.g., {"filename": "doc.pdf", "chunks_in_db": 5}
    message: str