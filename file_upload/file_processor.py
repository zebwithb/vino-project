#!/usr/bin/env python3
"""
VINO File Processor - Standalone Executable
Combines all file processing and database upload functionality into a single executable.

Usage:
    uv run python file_processor.py --help

"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Optional, List
import traceback

# Add the src directory to Python path for imports
current_dir = Path(__file__).parent
src_dir = current_dir.parent / "src"
sys.path.insert(0, str(src_dir))

try:
    from src.app.services.ingestion_service import IngestionService
    from src.app.services.vector_db_service import VectorDBService
    from src.app.services.supabase_service import SupabaseService
    from src.app.services.file_system_service import FileSystemService
    from src.app.core.config import Settings
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running this from the project root directory.")
    sys.exit(1)


class FileProcessorApp:
    """Main application class for the file processor."""
    
    def __init__(self):
        """Initialize the file processor with all required services."""
        try:
            self.settings = Settings()
            self.vector_db_service = None
            self.supabase_service = None
            self.file_system_service = None
            self.ingestion_service = None
            
            # Try to initialize ChromaDB service
            try:
                self.vector_db_service = VectorDBService()
            except Exception as e:
                print(f"⚠️ Warning: ChromaDB not available: {e}")
                print("Some features may be limited.")
            
            # Try to initialize Supabase service
            try:
                self.supabase_service = SupabaseService()
            except Exception as e:
                print(f"⚠️ Warning: Supabase not available: {e}")
            
            # Initialize file system service
            self.file_system_service = FileSystemService(self.supabase_service)
            
            # Initialize ingestion service
            self.ingestion_service = IngestionService(
                vector_db_service=self.vector_db_service,
                supabase_service=self.supabase_service,
                file_system_service=self.file_system_service
            )
            
            # Setup logging
            self.setup_logging()
            
        except Exception as e:
            print(f"❌ Critical error during initialization: {e}")
            raise
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('file_processor.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def process_single_file(self, file_path: str, source: str = "user_upload", 
                          collection_name: Optional[str] = None) -> bool:
        """
        Process a single file through the complete pipeline.
        
        Args:
            file_path: Path to the file to process
            source: Source type ("user_upload" or "system_upload")
            collection_name: Override collection name
            
        Returns:
            bool: Success status
        """
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"File not found: {file_path}")
                return False
            
            self.logger.info(f"🔄 Processing file: {file_path}")
            success = self.ingestion_service.ingest_single_file(file_path, source, collection_name)
            
            if success:
                self.logger.info(f"✅ Successfully processed: {file_path}")
            else:
                self.logger.error(f"❌ Failed to process: {file_path}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error processing file {file_path}: {str(e)}")
            self.logger.debug(traceback.format_exc())
            return False
    
    def process_directory(self, directory_path: str, source: str = "user_upload", 
                         move_processed: bool = True) -> bool:
        """
        Process all supported files in a directory.
        
        Args:
            directory_path: Path to directory containing files
            source: Source type ("user_upload" or "system_upload")
            move_processed: Whether to move processed files to processed directory
            
        Returns:
            bool: Success status
        """
        try:
            if not os.path.exists(directory_path):
                self.logger.error(f"Directory not found: {directory_path}")
                return False
            
            if not os.path.isdir(directory_path):
                self.logger.error(f"Path is not a directory: {directory_path}")
                return False
            
            self.logger.info(f"🔄 Processing directory: {directory_path}")
            
            # Determine target directory for processed files
            if move_processed:
                if source == "system_upload":
                    target_dir = self.settings.KB_DOCUMENTS_DIR
                else:
                    target_dir = self.settings.USER_UPLOADS_DIR
                
                success = self.ingestion_service.process_directory(
                    from_dir=directory_path,
                    to_dir=target_dir,
                    source=source
                )
            else:
                # Just process without moving files
                documents, metadatas, ids = self.ingestion_service.load_documents_from_directory(
                    directory_path, source
                )
                
                if documents:
                    collection_name = (self.settings.FRAMEWORKS_COLLECTION_NAME 
                                     if source == "system_upload" 
                                     else self.settings.USER_DOCUMENTS_COLLECTION_NAME)
                    
                    self.vector_db_service.add_documents(collection_name, documents, metadatas, ids)
                    
                    if self.supabase_service:
                        result = self.supabase_service.upload_documents_to_sql(metadatas, documents)
                        self.logger.info(f"Supabase upload result: {result}")
                    
                    success = True
                else:
                    success = False
            
            if success:
                self.logger.info(f"✅ Successfully processed directory: {directory_path}")
            else:
                self.logger.error(f"❌ Failed to process directory: {directory_path}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error processing directory {directory_path}: {str(e)}")
            self.logger.debug(traceback.format_exc())
            return False
    
    def process_default_directories(self) -> bool:
        """Process all default configured directories."""
        try:
            self.logger.info("🔄 Processing default directories...")
            result = self.ingestion_service.process_all_directories()
            self.logger.info(f"✅ {result}")
            return "complete" in result.lower()
            
        except Exception as e:
            self.logger.error(f"❌ Error processing default directories: {str(e)}")
            self.logger.debug(traceback.format_exc())
            return False
    
    def list_supported_files(self, directory_path: str) -> List[str]:
        """List all supported files in a directory."""
        try:
            supported_extensions = ['.txt', '.pdf', '.md']
            supported_files = []
            
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in supported_extensions):
                        supported_files.append(os.path.join(root, file))
            
            return supported_files
            
        except Exception as e:
            self.logger.error(f"❌ Error listing files in {directory_path}: {str(e)}")
            return []
    
    def show_status(self):
        """Show current system status and configuration."""
        print("\n" + "="*60)
        print("📋 VINO FILE PROCESSOR STATUS")
        print("="*60)
        
        # Project info
        print(f"🔧 Project: {self.settings.PROJECT_NAME} v{self.settings.VERSION}")
        print(f"📁 Project Root: {self.settings.PROJECT_ROOT}")
        
        # Database status
        print(f"\n💾 DATABASE CONFIGURATION:")
        print(f"   ChromaDB Path: {self.settings.CHROMA_DB_PATH}")
        print(f"   ChromaDB Server: {'Enabled' if self.settings.USE_CHROMA_SERVER else 'Disabled'}")
        if self.settings.USE_CHROMA_SERVER:
            print(f"   Server URL: {self.settings.CHROMA_SERVER_URL}")
        print(f"   ChromaDB Status: {'✅ Available' if self.vector_db_service else '❌ Not available'}")
        print(f"   Supabase: {'✅ Configured' if self.settings.SUPABASE_URL else '❌ Not configured'}")
        print(f"   Supabase Status: {'✅ Available' if self.supabase_service else '❌ Not available'}")
        
        # Collections
        print(f"\n📚 COLLECTIONS:")
        print(f"   Framework Documents: {self.settings.FRAMEWORKS_COLLECTION_NAME}")
        print(f"   User Documents: {self.settings.USER_DOCUMENTS_COLLECTION_NAME}")
        
        # Directory paths
        print(f"\n📂 DIRECTORIES:")
        print(f"   New Documents: {self.settings.NEW_DOCUMENTS_DIR}")
        print(f"   KB Documents: {self.settings.KB_DOCUMENTS_DIR}")
        print(f"   New User Uploads: {self.settings.NEW_USER_UPLOADS_DIR}")
        print(f"   User Uploads: {self.settings.USER_UPLOADS_DIR}")
        
        # Check directory status
        print(f"\n📊 DIRECTORY STATUS:")
        directories = [
            ("New Documents", self.settings.NEW_DOCUMENTS_DIR),
            ("KB Documents", self.settings.KB_DOCUMENTS_DIR),
            ("New User Uploads", self.settings.NEW_USER_UPLOADS_DIR),
            ("User Uploads", self.settings.USER_UPLOADS_DIR),
        ]
        
        for name, path in directories:
            if os.path.exists(path):
                files = self.list_supported_files(path)
                print(f"   {name}: ✅ ({len(files)} supported files)")
            else:
                print(f"   {name}: ❌ (Directory not found)")
        
        print("="*60 + "\n")


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="VINO File Processor - Process documents and upload to databases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --status                           # Show system status
  %(prog)s --file "document.pdf"              # Process single file
  %(prog)s --directory "C:/docs"              # Process directory
  %(prog)s --directory "C:/docs" --no-move   # Process without moving files
  %(prog)s --default                         # Process default directories
  %(prog)s --list "C:/docs"                  # List supported files
        """
    )
    
    # Main actions (mutually exclusive)
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        '--file', '-f',
        type=str,
        help='Process a single file'
    )
    action_group.add_argument(
        '--directory', '-d',
        type=str,
        help='Process all supported files in a directory'
    )
    action_group.add_argument(
        '--default',
        action='store_true',
        help='Process all default configured directories'
    )
    action_group.add_argument(
        '--status', '-s',
        action='store_true',
        help='Show system status and configuration'
    )
    action_group.add_argument(
        '--list', '-l',
        type=str,
        help='List all supported files in a directory'
    )
    
    # Options
    parser.add_argument(
        '--source',
        choices=['user_upload', 'system_upload'],
        default='user_upload',
        help='Source type for the documents (default: user_upload)'
    )
    parser.add_argument(
        '--collection',
        type=str,
        help='Override the target collection name'
    )
    parser.add_argument(
        '--no-move',
        action='store_true',
        help='Process files without moving them to processed directory'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Initialize the application
    try:
        app = FileProcessorApp()
        
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
    except Exception as e:
        print(f"❌ Failed to initialize application: {e}")
        sys.exit(1)
    
    # Execute the requested action
    success = True
    
    try:
        if args.status:
            app.show_status()
            
        elif args.file:
            success = app.process_single_file(args.file, args.source, args.collection)
            
        elif args.directory:
            success = app.process_directory(args.directory, args.source, not args.no_move)
            
        elif args.default:
            success = app.process_default_directories()
            
        elif args.list:
            files = app.list_supported_files(args.list)
            if files:
                print(f"\n📄 Found {len(files)} supported files in {args.list}:")
                for file in files:
                    print(f"   {file}")
            else:
                print(f"❌ No supported files found in {args.list}")
                success = False
        
    except KeyboardInterrupt:
        print("\n⚠️  Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)
    
    # Exit with appropriate code
    if success:
        print("\n✅ Operation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Operation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
