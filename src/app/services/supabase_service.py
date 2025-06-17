""" Program to upload a files to Supabase storage."""
import os

from ingestion_service import load_documents_from_directory
from file_system_service import upload_move_to_processed

from config import NEW_DOCUMENTS_DIR, NEW_USER_UPLOADS_DIR, KB_DOCUMENTS_DIR, USER_UPLOADS_DIR


def upload_documents_to_sql(metadata_list, content_list):
    """
    Upload multiple document metadata and content to Supabase.
    
    Args:
        metadata_list: List of combined metadata dictionaries (file + chunk metadata).
        content_list: List of chunk contents.
        
    Returns:
        str: Success message or error information
    """
    try:        # Group chunks by filename to store whole files instead of individual chunks
        files_data = {}
        
        # Group metadata and content by filename
        for i, meta in enumerate(metadata_list):
            if i >= len(content_list):
                print(f"Warning: Content missing for metadata at index {i}")
                continue
            
            # Validate metadata format
            if not isinstance(meta, dict):
                print(f"Warning: Expected dictionary but got {type(meta)} at index {i}")
                continue
                
            filename = meta.get('filename', 'unknown')
            
            if filename not in files_data:
                files_data[filename] = {
                    'file_metadata': meta,  # Use first chunk's metadata for file-level info
                    'chunks': []
                }
            
            # Add chunk content
            files_data[filename]['chunks'].append(content_list[i])
        
        # Process each file
        uploaded_count = 0
        for filename, file_data in files_data.items():
            meta = file_data['file_metadata']
            chunks = file_data['chunks']
            
            # Reconstruct full document from chunks
            full_document = '\n\n'.join(chunks)
            
            # Check if document already exists
            existing_doc = (
                supabase.table("filemetadata")
                .select("id")
                .eq("file_name", filename)
                .execute()
            )
            
            if existing_doc.data:
                print(f"Document {filename} already exists in database, skipping...")
                continue
                
            # Insert file metadata into the filemetadata table
            metadata_response = (
                supabase.table("filemetadata")
                .insert({
                    "file_name": filename,
                    "file_size": meta.get('file_size', 0),
                    "file_type": meta.get('file_type', 'unknown'),
                    "page_count": meta.get('page_count', 0),
                    "word_count": meta.get('word_count', 0),
                    "char_count": meta.get('char_count', 0),
                    "keywords": meta.get('keywords', []),
                    "source": meta.get('source', 'system_upload'),
                    "abstract": meta.get('abstract', '')
                })
                .execute()
            )
            
            # Check if metadata insertion was successful
            if not metadata_response.data:
                print(f"Failed to insert metadata for {filename}")
                continue
                
            # Get the ID of the newly inserted metadata record
            metadata_id = metadata_response.data[0]['id']
            
            # Insert full document content into the largeobject table
            content_response = (
                supabase.table("largeobject")
                .insert({
                    "oid": metadata_id,
                    "plain_text": full_document
                })
                .execute()
            )
            
            uploaded_count += 1
            print(f"Uploaded document: {filename} ({len(chunks)} chunks combined)")
        
        if uploaded_count > 0:
            return f"Successfully uploaded {uploaded_count} documents to database"
        else:
            return "No new documents were uploaded"
            
    except Exception as e:
        error_message = f"Error uploading documents to Supabase: {str(e)}"
        print(error_message)
        print(f"Error details: {type(e).__name__}")
        return error_message

def check_not_empty(directory):
    """
    Check if the directory is not empty.
    
    Args:
        directory: Path to the directory to check.
        
    Returns:
        bool: True if the directory is empty, False otherwise.
    """
    return  any(os.scandir(directory))

def process_directory(from_dir, to_dir, source="system_upload"):
    """
    Process documents from a specific directory and upload to Supabase.
    
    Args:
        from_dir: Path to the directory to process.
        to_dir: Path to move processed files.
        source: Source identifier for the documents.
        
    Returns:
        bool: True if documents were processed, False otherwise.
    """
    if check_not_empty(from_dir):
        documents, metadatas, ids, message = load_documents_from_directory(from_dir, source)
        try:
            upload_documents_to_sql(metadatas, documents)
            # Only move files if upload was successful
            upload_move_to_processed(from_dir, to_dir)
            print(f"Successfully processed documents from {from_dir}")
            return True
        except Exception as e:
            error_message = f"Error uploading documents from {from_dir} to Supabase: {str(e)}"
            print(error_message)
            # Don't move files on error - return False
            return False
    else:
        print(f"No documents to     upload from {from_dir}")
    return False

def upload_documents():
    """
    Upload documents from all configured directories to Supabase.
    
    Returns:
        str: Success message or error information
    """
    processed_docs = False
    
    # Process NEW_DOCUMENTS_DIR
    if process_directory(NEW_DOCUMENTS_DIR, KB_DOCUMENTS_DIR):
        processed_docs = True
        
    # Process NEW_USER_UPLOADS_DIR with source "user_uploads"
    if process_directory(NEW_USER_UPLOADS_DIR, USER_UPLOADS_DIR, source="user_uploads"):
        processed_docs = True
        
    if not processed_docs:
        return "No documents were processed from any directory."
    
    return "Document processing complete."

if __name__ == "__main__":
    result = upload_documents()
    print(result)