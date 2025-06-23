"""Supabase Service - Pure Supabase client operations."""
from typing import List, Dict, Any

from app.core.config import settings


class SupabaseService:
    """Pure Supabase client service for database and storage operations."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.client = None
        
        # Only initialize if credentials are provided
        if settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY:
            try:
                from supabase import create_client
                self.client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_ANON_KEY
                )
            except ImportError:
                print("Warning: Supabase package not installed. Install with: pip install supabase")
        else:
            print("Warning: Supabase credentials not configured")
    
    def upload_documents_to_sql(self, metadata_list: List[Dict[str, Any]], content_list: List[str]) -> str:
        """
        Upload multiple document metadata and content to Supabase.
        
        Args:
            metadata_list: List of combined metadata dictionaries (file + chunk metadata).
            content_list: List of chunk contents.
            
        Returns:
            str: Success message or error information
        """
        if not self.client:
            return "Supabase client not available. Check configuration and installation."
            
        try:
            # Group chunks by filename to store whole files instead of individual chunks
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
                    self.client.table("filemetadata")
                    .select("id")
                    .eq("file_name", filename)
                    .execute()
                )
                
                if existing_doc.data:
                    print(f"Document {filename} already exists in database, skipping...")
                    continue
                    
                # Insert file metadata into the filemetadata table
                metadata_response = (
                    self.client.table("filemetadata")
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
                self.client.table("largeobject").insert({
                    "oid": metadata_id,
                    "plain_text": full_document
                }).execute()
                
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
        
    def upload_file_to_storage(self, file_path: str, bucket_name: str) -> bool:
        """
        Upload a file to Supabase storage.
        
        Args:
            file_path: Path to the file to upload
            bucket_name: Name of the storage bucket
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.client:
            print("Warning: Supabase client not available")
            return False
            
        try:
            import os
            file_name = os.path.basename(file_path)
            
            with open(file_path, 'rb') as f:
                self.client.storage.from_(bucket_name).upload(file_name, f)
            
            # Check if upload was successful - Supabase typically returns success or throws exception
            print(f"Successfully uploaded: {file_name}")
            return True
                
        except Exception as e:
            print(f"Error uploading {file_path}: {e}")
            return False

    def check_document_exists(self, filename: str) -> bool:
        """
        Check if a document already exists in the database.
        
        Args:
            filename: Name of the file to check
            
        Returns:
            bool: True if document exists, False otherwise
        """
        if not self.client:
            return False
            
        try:
            existing_doc = (
                self.client.table("filemetadata")
                .select("id")
                .eq("file_name", filename)
                .execute()
            )
            return bool(existing_doc.data)
        except Exception as e:
            print(f"Error checking if document exists: {e}")
            return False