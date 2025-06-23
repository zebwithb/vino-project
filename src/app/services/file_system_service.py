"""File System Service - Handle file operations and movements."""
import os
from typing import Optional

from app.core.config import settings
from app.services.supabase_service import SupabaseService


class FileSystemService:
    """Service for file system operations including file movements and storage uploads."""
    
    def __init__(self, supabase_service: Optional[SupabaseService] = None):
        """Initialize with optional Supabase service for storage uploads."""
        self.supabase_service = supabase_service
    
    def move_files_to_processed(self, from_dir: str, to_dir: str, upload_to_storage: bool = True) -> str:
        """
        Move processed files from source directory to destination directory.
        Optionally upload to Supabase storage first.
        
        Args:
            from_dir: Source directory path
            to_dir: Destination directory path  
            upload_to_storage: Whether to upload to Supabase storage before moving
            
        Returns:
            str: Success message
        """
        if not os.path.exists(from_dir):
            return f"Source directory {from_dir} does not exist"
            
        # Ensure destination directory exists
        os.makedirs(to_dir, exist_ok=True)
        
        moved_count = 0
        failed_count = 0
        
        for file in os.listdir(from_dir):
            if os.path.isfile(os.path.join(from_dir, file)):
                source_path = os.path.join(from_dir, file)
                destination_path = os.path.join(to_dir, file)
                
                try:
                    # Upload to storage if requested and service is available
                    if upload_to_storage and self.supabase_service:
                        bucket_name = self._get_bucket_name(from_dir)
                        if bucket_name:
                            self.supabase_service.upload_file_to_storage(source_path, bucket_name)
                    
                    # Move the file
                    os.rename(source_path, destination_path)
                    moved_count += 1
                    print(f"Moved {file} from {from_dir} to {to_dir}")
                    
                except Exception as e:
                    print(f"Error processing {file}: {e}")
                    failed_count += 1
                    # Try to move file anyway, even if upload failed
                    try:
                        os.rename(source_path, destination_path)
                        print(f"Moved {file} despite processing error")
                    except Exception as move_error:
                        print(f"Failed to move {file}: {move_error}")
        
        if moved_count > 0:
            return f"Successfully moved {moved_count} files. {failed_count} files had errors."
        else:
            return f"No files were moved. {failed_count} files had errors."
    
    def _get_bucket_name(self, directory_path: str) -> Optional[str]:
        """
        Determine the appropriate Supabase storage bucket based on directory path.
        
        Args:
            directory_path: The source directory path
            
        Returns:
            str: Bucket name or None if no mapping exists
        """
        if directory_path == settings.NEW_DOCUMENTS_DIR:
            return 'knowledge-base'
        elif directory_path == settings.NEW_USER_UPLOADS_DIR:
            return 'user-uploads'
        else:
            return None
    
    def check_directory_not_empty(self, directory_path: str) -> bool:
        """
        Check if the directory is not empty.
        
        Args:
            directory_path: Path to the directory to check.
            
        Returns:
            bool: True if the directory is not empty, False otherwise.
        """
        try:
            return any(os.scandir(directory_path))
        except (OSError, FileNotFoundError):
            return False