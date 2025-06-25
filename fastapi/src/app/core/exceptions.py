"""Custom exceptions for the Vino application."""

class VinoError(Exception):
    """Base exception for all application-specific errors."""
    def __init__(self, message="An application error occurred."):
        self.message = message
        super().__init__(self.message)

class LLMError(VinoError):
    """Base exception for Language Model related errors."""
    pass

class LLMInitializationError(LLMError):
    """Raised when the Language Model fails to initialize."""
    def __init__(self, message="Failed to initialize the Language Model. Check API keys and configuration."):
        super().__init__(message)

class LLMInvocationError(LLMError):
    """Raised when invoking the Language Model chain fails."""
    def __init__(self, message="The request to the Language Model failed."):
        super().__init__(message)

class PromptGenerationError(VinoError):
    """Raised when a valid prompt template cannot be generated."""
    def __init__(self, message="Internal error: Could not generate a valid prompt for the current step."):
        super().__init__(message)

class SessionStorageError(VinoError):
    """Raised for errors related to persistent session storage."""
    def __init__(self, message="A problem occurred with the session storage service."):
        super().__init__(message)

class SupabaseServiceError(VinoError):
    """Custom exception for Supabase service errors."""
    def __init__(self, message="A problem occurred with the Supabase service."):
        super().__init__(message)

class VectorDBError(VinoError):
    """Raised for errors related to vector database operations."""
    def __init__(self, message="A problem occurred with the vector database."):
        super().__init__(message)

class DocumentProcessingError(VinoError):
    """Raised for errors during document processing."""
    def __init__(self, message="A problem occurred while processing documents."):
        super().__init__(message)
