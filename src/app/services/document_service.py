"""
Document Processing Service Module
"""

import os
import tiktoken

from app.core.config import settings
from app.schemas.models import ProcessingResult, DocumentMetadata

from app.services.chunking_service import chunk_single_file
from app.services.metadata_service import create_file_metadata




def process_document_content(file_path: str, content: str, page_count: int = 0, 
                           source: str = "system_upload") -> ProcessingResult:
    """
    Process document content into chunks with metadata and IDs.
    
    Args:
        file_path: Path to the source document
        content: Text content to be chunked
        page_count: Number of pages in the document (for PDFs)
        source: Source identifier for the document
        
    Returns:
        ProcessingResult containing document chunks, metadata, ids and chunk count
    """
    result = ProcessingResult()
    file_name = os.path.basename(file_path)
    
    # Skip if no content was extracted
    if not content.strip():
        print(f"Warning: No content extracted from {file_name}")
        return result
    
    file_extension = os.path.splitext(file_path)[1].lower()
    print(f"Processing file: {file_name} (type: {file_extension})")
    
    # Use fixed-size chunking for PDF files
    if file_extension == '.pdf':
        try:
            return _process_with_fixed_size_chunking(file_path, content, page_count, source)
        except Exception as e:
            print(f"Error using fixed-size chunking for PDF {file_name}: {e}")
            print("Falling back to simple processing...")
      # Try advanced chunking for other supported file types
    elif file_extension in settings.SUPPORTED_EXTENSIONS:
        try:
            return _process_with_advanced_chunking(file_path, content, page_count, source)
        except Exception as e:
            print(f"Error using advanced chunking for {file_name}: {e}")
            print("Falling back to simple processing...")
    
    # Fallback to simple processing
    return _process_with_simple_chunking(file_path, content, page_count, source)


def _process_with_advanced_chunking(file_path: str, content: str, page_count: int, 
                                  source: str) -> ProcessingResult:
    """
    Process document using advanced chunking from chunking.py module.
    
    Args:
        file_path: Path to the source document
        content: Text content of the document
        page_count: Number of pages in the document
        source: Source identifier for the document
        
    Returns:
        ProcessingResult with advanced chunking applied
    """
   
    file_name = os.path.basename(file_path)
    result = ProcessingResult()
    
    # Use the advanced chunking from chunking.py
    all_chunk_data = chunk_single_file(file_path)
    
    # Create file metadata once for the entire document
    file_metadata = create_file_metadata(file_path, content, page_count, source)
    
    # Process each chunk
    for chunk_data in all_chunk_data:
        result.chunk_all_texts.append(chunk_data.text)
        result.doc_metadatas.append(chunk_data.metadata)
        result.file_metadatas.append(file_metadata)
        result.chunk_ids.append(chunk_data.metadata.doc_id)
    
    print(f"Successfully processed {len(all_chunk_data)} chunks from {file_name}")
    return result


def _process_with_simple_chunking(file_path: str, content: str, page_count: int, 
                                source: str) -> ProcessingResult:
    """
    Process document using simple chunking (entire document as one chunk).
    
    Args:
        file_path: Path to the source document
        content: Text content of the document
        page_count: Number of pages in the document
        source: Source identifier for the document
        
    Returns:
        ProcessingResult with simple chunking applied
    """
    result = ProcessingResult()
    file_name = os.path.basename(file_path)
    
    # Add the full document as a single chunk
    result.chunk_all_texts.append(content)
    result.chunk_ids.append(file_name)
    
    # Create metadata
    file_metadata = create_file_metadata(file_path, content, page_count, source)
    doc_metadata = DocumentMetadata(
        doc_id=f"{os.path.splitext(file_name)[0]}_1",
        chunk_index=1,
        chunk_length=len(content),
        section="Full Document"
    )
    
    result.doc_metadatas.append(doc_metadata)
    result.file_metadatas.append(file_metadata)
    
    print(f"Processed 1 chunk (full document) from {file_name}")
    return result


def _process_with_fixed_size_chunking(file_path: str, content: str, page_count: int, 
                                    source: str, max_tokens: int = None, 
                                    overlap_tokens: int = None) -> ProcessingResult:
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
    # Use settings values if not provided
    if max_tokens is None:
        max_tokens = settings.MAX_CHUNK_TOKENS
    if overlap_tokens is None:
        overlap_tokens = settings.OVERLAP_TOKENS
        
    result = ProcessingResult()
    file_name = os.path.basename(file_path)
    doc_id_base = os.path.splitext(file_name)[0]
    
    # Initialize tokenizer
    try:
        encoding = tiktoken.encoding_for_model(settings.ENCODING_MODEL)
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

def _print_debug_info(file_name: str, result: ProcessingResult, file_path: str, 
                     page_count: int) -> None:
    """
    Print detailed debug information for processed chunk_all_texts.
    
    Args:
        file_name: Name of the processed file
        result: Processing result containing metadata
        file_path: Path to the source file
        page_count: Number of pages in the document
    """
    print("\n" + "="*60)
    print(f"DOCUMENT PROCESSED: {file_name}")
    print("="*60)
    print(f"Number of chunks: {len(result.chunk_all_texts)}")
    print(f"File size: {os.path.getsize(file_path):,} bytes")
    print(f"Page count: {page_count}")
    
    # Show sample of metadata for first chunk
    if result.file_metadatas:
        file_meta = result.file_metadatas[0]
        print(f"Word count: {file_meta.file_word_count:,}")
        print(f"Character count: {file_meta.file_char_count:,}")
        print(f"Keywords: {', '.join(file_meta.keywords)}")
        print(f"Abstract: {file_meta.abstract[:100]}...")
      # Show chunk size information for fixed-size chunking
    if result.doc_metadatas and len(result.chunk_all_texts) > 1:
        avg_chunk_length = sum(meta.chunk_length for meta in result.doc_metadatas) / len(result.doc_metadatas)
        print(f"Average chunk length: {avg_chunk_length:.0f} tokens")
        print(f"Chunk size range: {min(meta.chunk_length for meta in result.doc_metadatas)} - {max(meta.chunk_length for meta in result.doc_metadatas)} tokens")
    
    print("="*60 + "\n")