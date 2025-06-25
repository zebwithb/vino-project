"""Ingestion Service - Orchestrates the complete document ingestion pipeline."""
import os
import glob
from typing import List, Tuple, Optional

from app.core.config import settings
from app.services.extraction_service import extract_text_from_file
from app.services.document_service import process_document_content, _print_debug_info
from app.services.vector_db_service import VectorDBService
from app.services.supabase_service import SupabaseService
from app.services.file_system_service import FileSystemService


class IngestionService:
    """Orchestrates the complete document ingestion pipeline."""
    
    def __init__(self, 
                 vector_db_service: Optional[VectorDBService] = None,
                 supabase_service: Optional[SupabaseService] = None,
                 file_system_service: Optional[FileSystemService] = None):
        """
        Initialize the ingestion service with required dependencies.
        
        Args:
            vector_db_service: Service for vector database operations
            supabase_service: Service for Supabase operations
            file_system_service: Service for file system operations
        """
        self.vector_db_service = vector_db_service or VectorDBService()
        self.supabase_service = supabase_service or SupabaseService()
        self.file_system_service = file_system_service or FileSystemService(self.supabase_service)


    
    def _get_supported_files(self, directory_path: str) -> List[str]:
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

    def load_documents_from_directory(self, directory_path: Optional[str] = None, 
                                    source: str = "system_upload") -> Tuple[List[str], List[dict], List[str]]:
        """
        Read and process all supported documents from a directory.
        
        Args:
            directory_path: Path to the directory containing documents (defaults to NEW_DOCUMENTS_DIR)
            source: Source identifier for the documents
            
        Returns:
            Tuple of (documents, metadatas, ids)
        """
        if directory_path is None:
            directory_path = settings.NEW_DOCUMENTS_DIR
            
        all_documents = []
        all_metadatas = []
        all_ids = []    
        
        # Get all supported files in the directory
        file_paths = self._get_supported_files(directory_path)
        
        if not file_paths:
            print(f"No supported documents found in {directory_path}")
            return all_documents, all_metadatas, all_ids

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
                if settings.DEBUG_MODE:
                    _print_debug_info(file_name, result, file_path, page_count)
            
                # Log successful processing
                print(f"✓ Successfully loaded {len(result.chunk_all_texts)} chunks from: {file_name}")

            except Exception as e:
                print(f"✗ Error loading {file_name}: {e}")
                continue  # Continue with next file instead of stopping
        
        print(f"\nProcessing complete: {len(all_documents)} total chunks from {len(file_paths)} files")
        return all_documents, all_metadatas, all_ids

    def process_directory(self, from_dir: str, to_dir: str, source: str = "system_upload") -> bool:
        """
        Process documents from a specific directory - complete pipeline.
        
        Args:
            from_dir: Path to the directory to process
            to_dir: Path to move processed files
            source: Source identifier for the documents
            
        Returns:
            bool: True if documents were processed successfully, False otherwise
        """
        if not self.file_system_service.check_directory_not_empty(from_dir):
            print(f"No documents to upload from {from_dir}")
            return False
        
        try:
            # Step 1: Load and process documents
            documents, metadatas, ids = self.load_documents_from_directory(from_dir, source)
            
            if not documents:
                print(f"No documents were successfully processed from {from_dir}")
                return False            # Step 2: Store in vector database
            collection_name = settings.FRAMEWORKS_COLLECTION_NAME if source == "system_upload" else settings.USER_DOCUMENTS_COLLECTION_NAME
            self.vector_db_service.add_documents(collection_name, documents, metadatas, ids)
            
            # Step 3: Upload to Supabase (if available)
            if self.supabase_service:
                result = self.supabase_service.upload_documents_to_sql(metadatas, documents)
                print(f"Supabase upload result: {result}")
            
            # Step 4: Move files to processed directory
            move_result = self.file_system_service.move_files_to_processed(from_dir, to_dir, upload_to_storage=True)
            print(f"File movement result: {move_result}")
            
            print(f"Successfully processed documents from {from_dir}")
            return True
            
        except Exception as e:
            error_message = f"Error processing documents from {from_dir}: {str(e)}"
            print(error_message)
            return False

    def process_all_directories(self) -> str:
        """
        Process documents from all configured directories.
        
        Returns:
            str: Status message
        """
        processed_any = False
        
        # Process NEW_DOCUMENTS_DIR (framework documents)
        if self.process_directory(settings.NEW_DOCUMENTS_DIR, settings.KB_DOCUMENTS_DIR, source="system_upload"):
            processed_any = True
            
        # Process NEW_USER_UPLOADS_DIR (user uploaded documents)
        if self.process_directory(settings.NEW_USER_UPLOADS_DIR, settings.USER_UPLOADS_DIR, source="user_uploads"):
            processed_any = True
            
        if processed_any:
            return "Document processing complete."
        else:
            return "No documents were processed from any directory."

    def ingest_single_file(self, file_path: str, source: str = "system_upload", collection_name: Optional[str] = None) -> bool:
        """
        Ingest a single file through the complete pipeline.
        
        Args:
            file_path: Path to the file to ingest
            source: Source identifier for the document
            collection_name: Optional collection name override
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Process the single file
            documents, metadatas, ids = self.load_documents_from_directory(file_path, source)
            
            if not documents:
                print(f"No content extracted from {file_path}")
                return False
            
            # Determine collection
            if collection_name is None:
                collection_name = settings.FRAMEWORKS_COLLECTION_NAME if source == "system_upload" else settings.USER_DOCUMENTS_COLLECTION_NAME
              # Store in vector database
            self.vector_db_service.add_documents(collection_name, documents, metadatas, ids)
            
            # Upload to Supabase (if available)
            if self.supabase_service:
                result = self.supabase_service.upload_documents_to_sql(metadatas, documents)
                print(f"Supabase upload result: {result}")
            
            print(f"Successfully ingested file: {file_path}")
            return True
            
        except Exception as e:
            print(f"Error ingesting file {file_path}: {str(e)}")
            return False


# Legacy function for backward compatibility
def load_documents_from_directory(directory_path: Optional[str] = None, source: str = "system_upload") -> Tuple[List[str], List[dict], List[str]]:
    """Legacy function - use IngestionService class instead."""
    service = IngestionService()
    return service.load_documents_from_directory(directory_path, source)


