"""
Document Processing Service Module

This module provides document processing capabilities for the application.
It handles various document formats (PDF, TXT, MD, etc.) and converts them 
into structured chunks suitable for vector database storage and semantic search.

Main responsibilities:
- Extract text content from various document formats (PDF, text files)
- Split documents into manageable chunks with configurable overlap
- Generate metadata and unique IDs for each document chunk
- Batch process multiple documents from directories
- Handle file uploads and storage
- Provide document management utilities

The service integrates with the VectorDBService to enable semantic search
capabilities across processed document collections.
"""

import os
import glob
import PyPDF2
from typing import Tuple, Optional, List

from app import config
from app.models import ProcessingResult, DocumentMetadata

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text content from a PDF file using PyPDF2.
    
    Iterates through all pages of the PDF and concatenates the extracted text.
    Handles PDF files that may have text extraction issues gracefully.
    
    Args:
        pdf_path (str): Path to the PDF file to extract text from
        
    Returns:
        str: Extracted text content from all pages, empty string if extraction fails
        
    Note:
        - Some PDFs (especially scanned documents) may not extract text properly
        - Consider adding OCR capabilities for image-based PDFs in the future
        - Handles encrypted or corrupted PDFs by returning empty string
    """
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
    return text

def process_document_content(
    file_path: str,
    content: str,
    chunk_size: int = config.CHUNK_SIZE,
    chunk_overlap: int = config.CHUNK_OVERLAP
) -> ProcessingResult:
    """
    Process document content by splitting it into overlapping chunks.
    
    Takes raw document content and splits it into smaller, manageable chunks
    with configurable size and overlap. Each chunk receives unique metadata
    and IDs for storage in the vector database.
    
    Args:
        file_path (str): Path to the original document file
        content (str): Raw text content extracted from the document
        chunk_size (int, optional): Maximum size of each chunk in characters.
                                  Defaults to config.CHUNK_SIZE.
        chunk_overlap (int, optional): Number of overlapping characters between chunks.
                                     Defaults to config.CHUNK_OVERLAP.
                                     
    Returns:
        ProcessingResult: Object containing processed chunks, metadata, and IDs
        
    Note:
        - Chunk overlap helps maintain context between adjacent chunks
        - Empty content returns a ProcessingResult with zero chunks
        - Chunk IDs follow the format: {filename}_chunk_{number}
        - Metadata includes source path, filename, and chunk index
    """
    file_name = os.path.basename(file_path)
    result = ProcessingResult(filename=file_name)
    doc_id_base = os.path.splitext(file_name)[0].replace(" ", "_")

    if not content.strip():
        print(f"Warning: No content extracted from {file_name}")
        return result

    start_index = 0
    chunk_number = 1
    while start_index < len(content):
        end_index = min(start_index + chunk_size, len(content))
        chunk_text = content[start_index:end_index]

        metadata = DocumentMetadata(
            source=file_path,
            filename=file_name,
            chunk_index=chunk_number
        ).model_dump()

        result.documents_processed_texts.append(chunk_text)
        result.metadatas_for_db.append(metadata)
        result.ids_for_db.append(f"{doc_id_base}_chunk_{chunk_number}")

        start_index += chunk_size - chunk_overlap
        if start_index >= end_index and end_index < len(content): # Ensure progress if overlap is large
             start_index = end_index
        chunk_number += 1
    
    result.chunk_count = chunk_number - 1
    return result

def load_docs_from_directory_to_list(directory_path: str) -> ProcessingResult:
    """
    Load and process all supported documents from a directory.
    
    Recursively finds all PDF and text files in the specified directory,
    processes each document into chunks, and aggregates the results into
    a single ProcessingResult for batch operations.
    
    Args:
        directory_path (str): Path to directory containing documents to process
        
    Returns:
        ProcessingResult: Aggregated processing result containing all document chunks
        
    Supported file types:
        - PDF files (.pdf)
        - Text files (.txt)
        
    Note:
        - Skips files that cannot be processed due to format or access issues
        - Provides detailed logging for each processed document
        - Returns empty result if no valid documents found
        - Useful for bulk loading framework documentation or reference materials
    """
    aggregated_result = ProcessingResult(filename="aggregated")
    
    txt_files = glob.glob(os.path.join(directory_path, "*.txt"))
    pdf_files = glob.glob(os.path.join(directory_path, "*.pdf"))
    file_paths = txt_files + pdf_files

    for file_path in file_paths:
        try:
            content = ""
            if file_path.lower().endswith('.pdf'):
                content = extract_text_from_pdf(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

            if content.strip():
                result = process_document_content(file_path, content)
                aggregated_result.documents_processed_texts.extend(result.documents_processed_texts)
                aggregated_result.metadatas_for_db.extend(result.metadatas_for_db)
                aggregated_result.ids_for_db.extend(result.ids_for_db)
                aggregated_result.chunk_count += result.chunk_count
                print(f"Loaded {result.chunk_count} chunks from document: {os.path.basename(file_path)}")
            else:
                print(f"No content extracted from {os.path.basename(file_path)}")

        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            
    return aggregated_result

def load_single_document(file_path: str) -> Tuple[Optional[ProcessingResult], str]:
    """
    Load and process a single document file.
    
    Processes a single document file and returns the processing result along
    with a status message. Supports multiple file formats and provides
    detailed error reporting.
    
    Args:
        file_path (str): Path to the document file to process
        
    Returns:
        Tuple[Optional[ProcessingResult], str]: 
            - ProcessingResult object if successful, None if failed
            - Status message describing the result or error
            
    Supported file types:
        - PDF files (.pdf)
        - Text files (.txt, .md, .py, .js, .html, .css, .json)
        
    Example:
        result, message = load_single_document("/path/to/document.pdf")
        if result:
            print(f"Success: {message}")
            print(f"Processed {result.chunk_count} chunks")
        else:
            print(f"Error: {message}")
    """
    try:
        content = ""
        if file_path.lower().endswith('.pdf'):
            content = extract_text_from_pdf(file_path)
        elif file_path.lower().endswith(('.txt', '.md', '.py', '.js', '.html', '.css', '.json')): # Add more if needed
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        else:
            return None, f"Unsupported file type: {os.path.basename(file_path)}. Supported types are PDF and common text files."

        if not content.strip():
            return None, f"No content extracted from {os.path.basename(file_path)}"

        result = process_document_content(file_path, content)
        return result, f"Successfully processed {os.path.basename(file_path)} into {result.chunk_count} chunks"
    
    except Exception as e:
        return None, f"Error loading {file_path}: {str(e)}"

def store_uploaded_file(file_bytes: bytes, filename: str) -> Tuple[Optional[str], str]:
    """
    Store uploaded file bytes to the user uploads directory.
    
    Takes raw file bytes (typically from a web upload) and saves them to the
    configured user uploads directory. Creates the directory if it doesn't exist.
    
    Args:
        file_bytes (bytes): Raw bytes of the uploaded file
        filename (str): Original filename for the uploaded file
        
    Returns:
        Tuple[Optional[str], str]:
            - Full path to saved file if successful, None if failed
            - Status message describing the result or error
            
    Note:
        - Automatically creates the upload directory if it doesn't exist
        - Overwrites existing files with the same name
        - Consider adding filename sanitization and duplicate handling
        - File size limits should be enforced at the API level
        
    Example:
        file_path, message = store_uploaded_file(file_bytes, "document.pdf")
        if file_path:
            print(f"File saved to: {file_path}")
        else:
            print(f"Upload failed: {message}")
    """
    os.makedirs(config.USER_UPLOADS_DIR, exist_ok=True)
    destination_path = os.path.join(config.USER_UPLOADS_DIR, filename)
    try:
        with open(destination_path, 'wb') as f:
            f.write(file_bytes)
        return destination_path, f"File '{filename}' uploaded successfully."
    except Exception as e:
        return None, f"Error saving uploaded file '{filename}': {str(e)}"

def list_uploaded_files_in_dir() -> List[str]:
    """
    List all files in the user uploads directory.
    
    Returns a list of filenames (not full paths) for all files currently
    stored in the user uploads directory. Useful for displaying uploaded
    documents to users or for administrative purposes.
    
    Returns:
        List[str]: List of filenames in the uploads directory
                  Empty list if directory doesn't exist or is empty
                  
    Note:
        - Returns only filenames, not full paths
        - Filters out subdirectories, returns only files
        - Consider adding file metadata (size, upload date) in the future
        - Directory is created by store_uploaded_file() if needed
        
    Example:
        files = list_uploaded_files_in_dir()
        print(f"Found {len(files)} uploaded files:")
        for filename in files:
            print(f"  - {filename}")
    """
    if not os.path.exists(config.USER_UPLOADS_DIR):
        return []
    return [f for f in os.listdir(config.USER_UPLOADS_DIR) if os.path.isfile(os.path.join(config.USER_UPLOADS_DIR, f))]
