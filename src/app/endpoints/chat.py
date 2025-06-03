from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
from ..models import ChatRequest, ChatResponse
# Import the instance of ChatService
from ..services.chat_service import chat_service

router = APIRouter(
    prefix="/v1/chat", # Consistent with Reflex frontend expectation
    tags=["Chat"]
)

@router.post("", response_model=ChatResponse) # Empty path uses the router's prefix
async def handle_chat_request(request: ChatRequest = Body(...)):
    try:
        # Call your existing chat_service.process_query
        # Note: Your current chat_service.process_query signature is:
        # process_query(self, session_id: str, query_text: str, api_history_data: List[Dict[str, Any]], current_step_override: Optional[int] = None)
        # It returns: Tuple[str, List[Dict[str, Any]], int, Optional[str]]
        # (ai_response_content, api_history, current_step, planner)

        # TODO: You will need to modify `chat_service.process_query` to accept and utilize:
        # - request.selected_alignment
        # - request.explain_active
        # - request.tasks_active
        # - request.uploaded_file_context_name (for fetching context from the uploaded file)

        ai_response_content, _, updated_current_step, planner_str = chat_service.process_query(
            session_id=request.session_id,
            query_text=request.query_text,
            api_history_data=request.history,
            current_step_override=request.current_step
        )
        
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