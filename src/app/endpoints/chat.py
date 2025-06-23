import uuid
from fastapi import APIRouter, Body, Depends, Query
from typing import Optional
from pydantic import BaseModel
from ..schemas.models import QueryRequest as ChatRequest, QueryResponse as ChatResponse
from ..services.chat_service import ChatService
from ..dependencies import get_chat_service

router = APIRouter(
    prefix="/v1/chat",
    tags=["Chat"]
)

# Simple chat request model for basic conversations
class SimpleChatRequest(BaseModel):
    """Simplified chat request for basic conversations."""
    message: str
    session_id: Optional[str] = None
    file_context: Optional[str] = None  # Optional file to chat about

class SimpleChatResponse(BaseModel):
    """Simplified chat response."""
    response: str
    session_id: str

@router.post("", response_model=ChatResponse) # Empty path uses the router's prefix
async def handle_chat_request(
    request: ChatRequest = Body(...),
    chat_service: ChatService = Depends(get_chat_service),
    session_id: Optional[str] = Query(None)  # Accept session_id as query parameter
):
    # Call the enhanced chat_service.process_query with all parameters
    # FastAPI will automatically handle any custom exceptions via exception handlers in main.py
    
    # Use session_id from query parameter if provided, otherwise use the one in request body
    actual_session_id = session_id or request.session_id
    
    ai_response_content, updated_history, updated_current_step, planner_str = chat_service.process_query(
        session_id=actual_session_id,
        query_text=request.query_text,
        api_history_data=request.history,
        current_step_override=request.current_step,
        selected_alignment=request.selected_alignment,
        explain_active=request.explain_active,
        tasks_active=request.tasks_active,
        uploaded_file_context_name=request.uploaded_file_context_name
    )
    
    return ChatResponse(
        response=ai_response_content,
        current_step=updated_current_step,
        planner_details=planner_str
    )

@router.post("/simple", response_model=SimpleChatResponse)
async def simple_chat(
    request: SimpleChatRequest = Body(...),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Simple chat endpoint for basic conversations with the LLM.
    
    This endpoint provides a simplified interface for chatting with the AI
    without needing to manage all the advanced features like steps, planner, etc.
    """
    
    # Generate session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())
    
    # Call the full chat service with sensible defaults
    ai_response_content, _, _, _ = chat_service.process_query(
        session_id=session_id,
        query_text=request.message,
        api_history_data=[],  # Empty history for simple mode
        current_step_override=None,  # Use default step progression
        selected_alignment=None,
        explain_active=False,
        tasks_active=False,
        uploaded_file_context_name=request.file_context
    )
    
    return SimpleChatResponse(
        response=ai_response_content,
        session_id=session_id
    )