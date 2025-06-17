""""Ingestion Service
deals with sources of documents
"""
import os
import glob
import tiktoken

from typing import List, Tuple
from app.schemas.models import ProcessingResult, DocumentMetadata
from app.config import NEW_DOCUMENTS_DIR, DEBUG_MODE
from app.config import ENCODING_MODEL, MAX_CHUNK_TOKENS, OVERLAP_TOKENS

from app.services.extraction_service import extract_text_from_file
from app.services.document_service import process_document_content, _print_debug_info
from app.services.metadata_service import create_file_metadata


def _get_supported_files(directory_path: str) -> List[str]:
    """
    Get all supported document files from a directory or check if a single file is supported.
    
    Args:
        directory_path: Path to the directory to scan or path to a single file
        
    Returns:
        List of file paths for supported document types
    """
    file_patterns = ["*.txt", "*.pdf", "*.md"]
    all_files = []
    
    # Check if it's a single file path
    if os.path.isfile(directory_path):
        # Check if the file has a supported extension
        _, ext = os.path.splitext(directory_path)
        if ext.lower() in ['.txt', '.pdf', '.md']:
            return [directory_path]
        else:
            return []
    
    # It's a directory, use glob patterns
    for pattern in file_patterns:
        files = glob.glob(os.path.join(directory_path, pattern))
        all_files.extend(files)
    
    return all_files


def load_documents_from_directory(directory_path: str = NEW_DOCUMENTS_DIR, 
                                source: str = "system_upload") -> Tuple[List[str], List[dict], List[str]]:
    """
    Read and process all supported documents from a directory.
    
    Args:
        directory_path: Path to the directory containing documents
        source: Source identifier for the documents
        
    Returns:
        Tuple of (documents, metadatas, ids)
    """
    all_documents = []
    all_metadatas = []
    all_ids = []    
    
    # Get all supported files in the directory
    file_paths = _get_supported_files(directory_path)
    
    if not file_paths:
        print(f"No supported documents found in {directory_path}")
        return all_documents, all_metadatas, all_ids, "No supported documents found"

    print(f"Found {len(file_paths)} documents to process in {directory_path}")

    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        try:
            # Extract text content based on file type
            content, page_count = extract_text_from_file(file_path)
            
            # Process the document content
            result = process_document_content(file_path, content, page_count, source)
            
            # Aggregate results
            all_documents.extend(result.chunk_all_texts)
            all_ids.extend(result.chunk_ids)
            
            # Convert Pydantic models to dictionaries for ChromaDB
            for doc_meta, file_meta in zip(result.doc_metadatas, result.file_metadatas):
                combined_metadata = {
                    **doc_meta.model_dump(),  # Document-specific metadata
                    **file_meta.model_dump()  # File-level metadata
                }
                all_metadatas.append(combined_metadata)
            
            # Debug output if enabled
            if DEBUG_MODE:
                _print_debug_info(file_name, result, file_path, page_count)
        
            # Log successful processing
            print(f"✓ Successfully loaded {len(result.chunk_all_texts)} chunks from: {file_name}")

        except Exception as e:
            print(f"✗ Error loading {file_name}: {e}")
            continue  # Continue with next file instead of stopping
    
    print(f"\nProcessing complete: {len(all_documents)} total chunks from {len(file_paths)} files")
    return all_documents, all_metadatas, all_ids, "Successfully processed all documents."


