from fastapi import APIRouter, HTTPException, Body, Depends
from ..schemas.models import QueryRequest as ChatRequest, QueryResponse as ChatResponse
from ..services.chat_service import ChatService
from ..dependencies import get_chat_service
from ..core.exceptions import (
    LLMInitializationError,
    LLMInvocationError, 
    PromptGenerationError,
    SessionStorageError,
    VinoError
)

router = APIRouter(
    prefix="/v1/chat",
    tags=["Chat"]
)

@router.post("", response_model=ChatResponse) # Empty path uses the router's prefix
async def handle_chat_request(
    request: ChatRequest = Body(...),
    chat_service: ChatService = Depends(get_chat_service)
):
    try:
        # Call the enhanced chat_service.process_query with all parameters
        ai_response_content, updated_history, updated_current_step, planner_str = chat_service.process_query(
            session_id=request.session_id,
            query_text=request.query_text,
            api_history_data=request.history,
            current_step_override=request.current_step,
            selected_alignment=request.selected_alignment,
            explain_active=request.explain_active,
            tasks_active=request.tasks_active,
            uploaded_file_context_name=request.uploaded_file_context_name        )
        
        return ChatResponse(
            response=ai_response_content,
            current_step=updated_current_step,
            planner_details=planner_str
        )
    
    except LLMInitializationError as e:
        raise HTTPException(status_code=503, detail=f"Language model service unavailable: {e.message}")
    except LLMInvocationError as e:
        raise HTTPException(status_code=503, detail=f"Language model request failed: {e.message}")
    except PromptGenerationError as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e.message}")
    except SessionStorageError as e:
        raise HTTPException(status_code=503, detail=f"Session service unavailable: {e.message}")
    except VinoError as e:
        # Catch other custom application errors
        raise HTTPException(status_code=400, detail=f"Application error: {e.message}")
    except HTTPException:
        raise # Re-raise HTTPException to ensure correct status code and detail
    except Exception as e:
        # Log unexpected errors with full traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error in /v1/chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected internal server error occurred")