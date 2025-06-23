from typing import List, Dict, Any, Optional, Tuple

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage

from app.core.config import settings
from app.prompt_engineering.builder import get_universal_matrix_prompt
from app.services.vector_db_service import VectorDBService

# Forward declaration to avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.services.session_storage_service import SessionStorageService

class ChatService:
    def __init__(self, vector_db_service: Optional[VectorDBService] = None, session_storage_service: Optional["SessionStorageService"] = None):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL_NAME,
            api_key=settings.GOOGLE_API_KEY,
            temperature=settings.LLM_TEMPERATURE,
            # max_tokens=settings.LLM_MAX_TOKENS,
            # timeout=settings.LLM_TIMEOUT,
            max_retries=settings.LLM_MAX_RETRIES,
            convert_system_message_to_human=True # Gemini API prefers this for system messages
        )
        # Use provided services or create new ones
        self.vector_db_service = vector_db_service or VectorDBService()
        self.session_storage_service = session_storage_service
          # Keep in-memory fallback for when persistent storage is not available
        self.conversation_history: Dict[str, List[BaseMessage]] = {} # Keyed by a session_id
        self.current_process_step: Dict[str, int] = {}
        self.planner_details: Dict[str, Optional[str]] = {}

    def _get_session_data(self, session_id: str) -> Tuple[List[BaseMessage], int, Optional[str]]:
        """Get session data from persistent storage or fallback to memory."""
        if self.session_storage_service:
            # Use persistent storage
            try:
                return self.session_storage_service.get_session_data(session_id)
            except Exception as e:
                print(f"Error loading session from persistent storage, falling back to memory: {e}")
        
        # Fallback to in-memory storage
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
            self.current_process_step[session_id] = 1
            self.planner_details[session_id] = None
        return (
            self.conversation_history[session_id],
            self.current_process_step[session_id],
            self.planner_details[session_id]
        )

    def _update_session_data(self, session_id: str, history: List[BaseMessage], step: int, planner: Optional[str]):
        """Update session data in persistent storage and memory fallback."""
        if self.session_storage_service:
            # Use persistent storage
            try:
                success = self.session_storage_service.update_session_data(session_id, history, step, planner)
                if success:
                    return  # Successfully saved to persistent storage
                else:
                    print("Failed to save to persistent storage, falling back to memory")
            except Exception as e:
                print(f"Error saving session to persistent storage, falling back to memory: {e}")
        
        # Fallback to in-memory storage
        self.conversation_history[session_id] = history
        self.current_process_step[session_id] = step
        self.planner_details[session_id] = planner

    def delete_session(self, session_id: str) -> bool:
        """Delete a session from storage."""
        success = False
        
        if self.session_storage_service:
            success = self.session_storage_service.delete_session(session_id)
        
        # Also clean up from memory
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]
        if session_id in self.current_process_step:
            del self.current_process_step[session_id]
        if session_id in self.planner_details:
            del self.planner_details[session_id]
            
        return success

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session metadata without loading full conversation."""
        if self.session_storage_service:
            return self.session_storage_service.get_session_info(session_id)
        
        # Fallback to checking memory
        if session_id in self.conversation_history:
            return {
                "session_id": session_id,
                "current_step": self.current_process_step.get(session_id, 1),
                "planner_details": self.planner_details.get(session_id),
                "message_count": len(self.conversation_history[session_id]),
                "storage_type": "memory"
            }
        return None

    def _convert_api_history_to_langchain(self, history_data: List[Dict[str, Any]]) -> List[BaseMessage]:
        messages = []
        for item in history_data:
            role = item.get("role")
            content = item.get("content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
            elif role == "system": # If you ever pass system messages this way
                messages.append(SystemMessage(content=content))
        return messages

    def _convert_langchain_history_to_api(self, langchain_history: List[BaseMessage]) -> List[Dict[str, Any]]:
        api_history = []
        for msg in langchain_history:
            if isinstance(msg, HumanMessage):
                api_history.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                api_history.append({"role": "assistant", "content": msg.content})
            elif isinstance(msg, SystemMessage):
                 api_history.append({"role": "system", "content": msg.content})
        return api_history
    
# TODO Handle when it is None
    def _add_results_to_context(self, results: Dict[str, Optional[List[Any]]], section_title: str, context: str = "") -> Tuple[str, bool]:
        has_results = False
        if results and results.get('documents') and results['documents'] is not None and results['documents'][0]: # ChromaDB returns list of lists
            context += f"\n--- {section_title} ---\n"
            for i, doc_content in enumerate(results['documents'][0]):
                metadata = {}
                if results.get('metadatas') and results['metadatas'] is not None and results['metadatas'][0] is not None:
                    metadata = results['metadatas'][0][i] if i < len(results['metadatas'][0]) else {}
                source = metadata.get('filename', "Unknown source")
                context += f"\n--- From {source} (Chunk {metadata.get('chunk_index', 'N/A')}) ---\n{doc_content}\n"
            has_results = True
        return context, has_results    
    
    def process_query(
        self, 
        session_id: str, 
        query_text: str, 
        api_history_data: List[Dict[str, Any]], 
        current_step_override: Optional[int] = None,
        selected_alignment: Optional[str] = None,
        explain_active: Optional[bool] = False,
        tasks_active: Optional[bool] = False,
        uploaded_file_context_name: Optional[str] = None
    ) -> Tuple[str, List[Dict[str, Any]], int, Optional[str]]:
        history, current_step, planner = self._get_session_data(session_id)

        if current_step_override is not None and 1 <= current_step_override <= 6:
            current_step = current_step_override
            if current_step_override == 1:  # Reset history if jumping back to step 1
                history = []
                planner = None        # Handle uploaded file context
        file_context = ""
        if uploaded_file_context_name:
            try:
                # Query vector database for content specifically from the uploaded file
                file_results = self.vector_db_service.query_collection(
                    collection_name=settings.USER_DOCUMENTS_COLLECTION_NAME,
                    query_text=query_text,
                    n_results=10,  # Get more results since we're focusing on one file
                    where={"filename": uploaded_file_context_name}  # Filter by filename
                )
                
                # Add file-specific context
                file_context, has_file_results = self._add_results_to_context(
                    file_results, 
                    f"Relevant Information From {uploaded_file_context_name}", 
                    file_context
                )
                
                if not has_file_results:
                    file_context = f"\n--- File Context from {uploaded_file_context_name} ---\n"
                    file_context += "[No relevant content found in this file for your query.]\n"
                
                print(f"File context loaded for: {uploaded_file_context_name}")
            except Exception as e:
                print(f"Error loading file context: {e}")
                file_context = f"\n--- File Context from {uploaded_file_context_name} ---\n"
                file_context += f"[Error loading file context: {str(e)}]\n"

        # Handle special modes
        mode_context = ""
        if explain_active:
            mode_context += "\n--- EXPLAIN MODE ACTIVE ---\n"
            mode_context += "Please provide explanations for your responses and reasoning.\n"
        
        if tasks_active:
            mode_context += "\n--- TASKS MODE ACTIVE ---\n"
            mode_context += "Please generate actionable tasks based on the conversation.\n"
            
        if selected_alignment:
            mode_context += f"\n--- ALIGNMENT: {selected_alignment.upper()} ---\n"
            mode_context += f"Please respond with a {selected_alignment.lower()} approach.\n"        # Query vector databases using the service instance
        # When file context is specified, reduce general user document search
        user_search_results = 2 if not uploaded_file_context_name else 1
        
        fw_results = self.vector_db_service.query_collection(
            collection_name=settings.FRAMEWORKS_COLLECTION_NAME,
            query_text=query_text, n_results=2
        )
        user_results = self.vector_db_service.query_collection(
            collection_name=settings.USER_DOCUMENTS_COLLECTION_NAME,
            query_text=query_text, n_results=user_search_results
        )

        combined_context = ""
        combined_context, _ = self._add_results_to_context(fw_results, "Relevant Framework Information", combined_context)
        
        # Only add general user document context if no specific file context was requested
        if not uploaded_file_context_name:
            combined_context, _ = self._add_results_to_context(user_results, "Relevant Information From Your Documents", combined_context)
        
        # Add mode and file context to combined context (file context takes priority)
        combined_context = file_context + combined_context + mode_context
        
        # Langchain history should be the actual conversation flow
        # The api_history_data might be what the client *thinks* the history is.
        # For simplicity now, we'll trust the client's history if provided, otherwise use server's.
        # A robust solution would reconcile or always use server-side history.
        if api_history_data:
             history = self._convert_api_history_to_langchain(api_history_data)
        
        # Get prompt from prompt_engineering
        # Note: `get_universal_matrix_prompt` expects `history` to be passed to `invoke` later
        # So we pass an empty list or the actual history to the builder if it uses it directly.
        # The current builder seems to use a MessagesPlaceholder.
        prompt_template = get_universal_matrix_prompt(
            current_step=current_step,
            history=[], # Placeholder, actual history passed in invoke
            question=query_text,
            step_context="", # Placeholder for now, can be enhanced
            general_context=combined_context.strip(),
            planner_state=planner
        )

        if not prompt_template:
            error_msg = f"Error: Could not generate prompt for step {current_step}."
            print(error_msg)
            # Return current state without advancing or adding to history
            return error_msg, self._convert_langchain_history_to_api(history), current_step, planner

        try:
            # Construct the chain for this call
            # The `history` variable here is the list of Langchain BaseMessage objects
            chain = prompt_template | self.llm
            
            # Invoke the chain
            # The `history` argument for `invoke` maps to the `MessagesPlaceholder(variable_name="history")`
            response_message = chain.invoke({
                "history": history, # Pass the actual conversation history here
                "question": query_text, # Already in human message of template
                # other variables expected by your specific prompt template structure
                # "step_context": "", # if used by template
                # "general_context": combined_context.strip(), # if used by template
                # "planner_state": planner, # if used by template
                # "current_step": current_step # if used by template
            })
            ai_response_content = response_message.content

            # Update history
            history.append(HumanMessage(content=query_text))
            history.append(AIMessage(content=ai_response_content))

            # Basic logic to advance step or update planner (can be made more sophisticated)
            # This is a placeholder; VINO's logic for step transition and planner updates
            # would be more complex, potentially based on LLM output.
            if f"Proceed to Step {current_step + 1}" in ai_response_content and current_step < 6:
                current_step += 1

            if current_step == 3 and "PLANNER DEFINED:" in ai_response_content: # Example trigger
                # Extract planner (this is a simplistic example)
                try:
                    if isinstance(ai_response_content, str):
                        planner = ai_response_content.split("PLANNER DEFINED:")[1].strip()
                except IndexError:
                    pass # Planner not found or format incorrect            self._update_session_data(session_id, history, current_step, planner)
            return str(ai_response_content), self._convert_langchain_history_to_api(history), current_step, planner
        
        except Exception as e:
            print(f"Error during LLM chain invocation: {e}")
            # Return current state without advancing or adding to history
            return f"Error: Failed to get response from language model. {str(e)}", self._convert_langchain_history_to_api(history), current_step, planner