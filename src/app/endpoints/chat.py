from fastapi import APIRouter, HTTPException, Body, Depends
from ..schemas.models import QueryRequest as ChatRequest, QueryResponse as ChatResponse
from ..services.chat_service import ChatService
from ..dependencies import get_chat_service

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
        
        if not ai_response_content: # Or based on some error indicator from process_query
            raise HTTPException(status_code=404, detail="Could not generate an answer.")
        
        return ChatResponse(
            response=ai_response_content,
            current_step=updated_current_step,
            planner_details=planner_str
        )
    except HTTPException:
        raise # Re-raise HTTPException to ensure correct status code and detail
    except Exception as e:
        print(f"Error in /v1/chat endpoint: {e}")
        # Consider logging the full traceback here for debugging
        raise HTTPException(status_code=500, detail=f"Internal server error during chat processing: {str(e)}")