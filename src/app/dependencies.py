from functools import lru_cache
from app.services.vector_db_service import VectorDBService
from app.services.chat_service import ChatService
from app.services.supabase_service import SupabaseService
from app.services.file_system_service import FileSystemService
from app.services.ingestion_service import IngestionService

# The @lru_cache decorator ensures that each function is only called once,
# effectively creating a singleton instance of each service.

@lru_cache()
def get_vector_db_service() -> VectorDBService:
    """Returns a singleton instance of the VectorDBService."""
    return VectorDBService()

@lru_cache()
def get_chat_service() -> ChatService:
    """Returns a singleton instance of the ChatService."""
    return ChatService()

@lru_cache()
def get_supabase_service() -> SupabaseService:
    """Returns a singleton instance of the SupabaseService."""
    return SupabaseService()

@lru_cache()
def get_file_system_service() -> FileSystemService:
    """Returns a singleton instance of the FileSystemService."""
    return FileSystemService(get_supabase_service())

@lru_cache()
def get_ingestion_service() -> IngestionService:
    """Returns a singleton instance of the IngestionService."""
    return IngestionService(
        vector_db_service=get_vector_db_service(),
        supabase_service=get_supabase_service(),
        file_system_service=get_file_system_service()
    )
