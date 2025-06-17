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



def _process_with_fixed_size_chunking(file_path: str, content: str, page_count: int, 
                                    source: str, max_tokens: int = MAX_CHUNK_TOKENS, 
                                    overlap_tokens: int = OVERLAP_TOKENS) -> ProcessingResult:
    """
    Process document using fixed-size chunking strategy based on tokens.
    
    Args:
        file_path: Path to the source document
        content: Text content of the document
        page_count: Number of pages in the document
        source: Source identifier for the document
        max_tokens: Maximum tokens per chunk
        overlap_tokens: Number of tokens to overlap between chunks
        
    Returns:
        ProcessingResult with fixed-size chunking applied
    """
    result = ProcessingResult()
    file_name = os.path.basename(file_path)
    doc_id_base = os.path.splitext(file_name)[0]
    
    # Initialize tokenizer
    try:
        encoding = tiktoken.encoding_for_model(ENCODING_MODEL)
    except Exception:
        # Fallback to a default encoding if model not found
        encoding = tiktoken.get_encoding("cl100k_base")
    
    # Create file metadata once for the entire document
    file_metadata = create_file_metadata(file_path, content, page_count, source)
    
    # Tokenize the entire content
    tokens = encoding.encode(content)
    total_tokens = len(tokens)
    
    if total_tokens == 0:
        print(f"Warning: No tokens found in {file_name}")
        return result
    
    print(f"Processing {file_name}: {total_tokens} tokens total")
    
    # Implement token-based fixed-size chunking
    start_token = 0
    chunk_number = 1
    
    while start_token < total_tokens:
        # Calculate end token for this chunk
        end_token = min(start_token + max_tokens, total_tokens)
        
        # Extract chunk tokens and decode back to text
        chunk_tokens = tokens[start_token:end_token]
        chunk_text = encoding.decode(chunk_tokens)
        
        # Skip empty chunks
        if not chunk_text.strip():
            start_token += max_tokens - overlap_tokens
            continue
        
        # Create DocumentMetadata object
        doc_metadata = DocumentMetadata(
            doc_id=f"{doc_id_base}_chunk_{chunk_number}",
            chunk_index=chunk_number,
            chunk_length=len(chunk_tokens),  # Store token count instead of character count
            section=f"Chunk {chunk_number}"
        )
        
        result.chunk_all_texts.append(chunk_text)
        result.doc_metadatas.append(doc_metadata)
        result.file_metadatas.append(file_metadata)
        result.chunk_ids.append(f"{doc_id_base}_chunk_{chunk_number}")
        
        # Move to next chunk with overlap
        start_token += max_tokens - overlap_tokens
        chunk_number += 1
    
    print(f"Successfully processed {len(result.chunk_all_texts)} token-based chunks from {file_name}")
    print(f"Average tokens per chunk: {total_tokens / len(result.chunk_all_texts):.0f}")
    return result