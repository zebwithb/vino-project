from typing import List, Dict, Any, Optional, Tuple

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage

from app import config
from app.prompt_engineering.builder import get_universal_matrix_prompt
from app.services.vector_db_service import vector_db_service # Import the instance

class ChatService:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=config.LLM_MODEL_NAME,
            api_key=config.GOOGLE_API_KEY,
            temperature=config.LLM_TEMPERATURE,
            # max_tokens=config.LLM_MAX_TOKENS, # Often not needed for Chat models, can cause issues
            # timeout=config.LLM_TIMEOUT,
            max_retries=config.LLM_MAX_RETRIES,
            convert_system_message_to_human=True # Gemini API prefers this for system messages
        )
        # In-memory state - for a real app, this should be managed per-session/user
        self.conversation_history: Dict[str, List[BaseMessage]] = {} # Keyed by a session_id
        self.current_process_step: Dict[str, int] = {}
        self.planner_details: Dict[str, Optional[str]] = {}

    def _get_session_data(self, session_id: str) -> Tuple[List[BaseMessage], int, Optional[str]]:
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
        self.conversation_history[session_id] = history
        self.current_process_step[session_id] = step
        self.planner_details[session_id] = planner

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
                context += f"\n--- From {source} (Chunk {metadata.get('chunk', 'N/A')}) ---\n{doc_content}\n"
            has_results = True
        return context, has_results

    def process_query(self, session_id: str, query_text: str, api_history_data: List[Dict[str, Any]], current_step_override: Optional[int] = None) -> Tuple[str, List[Dict[str, Any]], int, Optional[str]]:
        history, current_step, planner = self._get_session_data(session_id)

        if current_step_override is not None and 1 <= current_step_override <= 6 :
            current_step = current_step_override
            if current_step_override == 1: # Reset history if jumping back to step 1
                history = []
                planner = None


        # Query vector databases
        fw_results = vector_db_service.query_collection(
            collection_name=config.FRAMEWORKS_COLLECTION_NAME,
            query_texts=[query_text], n_results=2
        )
        user_results = vector_db_service.query_collection(
            collection_name=config.USER_DOCUMENTS_COLLECTION_NAME,
            query_texts=[query_text], n_results=2
        )

        combined_context = ""
        combined_context, _ = self._add_results_to_context(fw_results, "Relevant Framework Information", combined_context)
        combined_context, _ = self._add_results_to_context(user_results, "Relevant Information From Your Documents", combined_context)
        
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
                    pass # Planner not found or format incorrect

            self._update_session_data(session_id, history, current_step, planner)
            return str(ai_response_content), self._convert_langchain_history_to_api(history), current_step, planner

        except Exception as e:
            print(f"Error during LLM chain invocation: {e}")
            # Return current state without advancing or adding to history
            return f"Error: Failed to get response from language model. {str(e)}", self._convert_langchain_history_to_api(history), current_step, planner

# Instantiate the service
chat_service = ChatService()