import reflex as rx
from typing import List, TypedDict, Optional, Dict, Any, Literal
import httpx # For making HTTP requests
import os
import uuid # For generating session IDs

# Define the FastAPI backend URL (consider making this an environment variable)
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")

AlignmentOption = Literal[
    "Guidance", "Criticism", "Advising", "Validate"
]

class Message(TypedDict):
    text: str
    is_ai: bool


class ChatState(rx.State):
    messages: List[Message] = []
    processing: bool = False
    input_message: str = ""

    # VINO specific state
    session_id: Optional[str] = None
    current_vino_step: int = 1
    current_planner_details: Optional[str] = None
    proposed_next_step: Optional[int] = None
    confirmation_in_progress: bool = False

    # New UI features state
    alignment_options: List[AlignmentOption] = [
        "Guidance",
        "Criticism",
        "Advising",
        "Validate",
    ]
    selected_alignment: AlignmentOption = "Guidance"
    explain_active: bool = False
    tasks_active: bool = False
    uploaded_file_name: Optional[str] = "" # Name of the file displayed in UI
    # File context is passed to backend via uploaded_file_context_name field
    show_prompt_toolbox: bool = False

    @rx.var
    def has_session(self) -> bool:
        return self.session_id is not None

    @rx.var
    def message_count(self) -> int:
        """Get the current message count - useful for triggering scroll effects"""
        return len(self.messages)

    @rx.event
    def force_navbar_refresh(self):
        """Force a navbar refresh by triggering a state change"""
        print(f"Forcing navbar refresh for step {self.current_vino_step}")
        # Trigger a state update that will cause the navbar to re-render
        return rx.call_script("console.log('Navbar refresh triggered');")
        """Force a navbar refresh by triggering a state change"""
        print(f"Forcing navbar refresh for step {self.current_vino_step}")
        # Trigger a state update that will cause the navbar to re-render
        return rx.call_script("console.log('Navbar refresh triggered');")

    @rx.var
    def current_step_display(self) -> int:
        """Reactive property for current step to ensure navbar updates"""
        print(f"Navbar: current_step_display accessed, returning step {self.current_vino_step}")
        return self.current_vino_step

    @rx.event
    def toggle_prompt_toolbox(self):
        self.show_prompt_toolbox = (
            not self.show_prompt_toolbox
        )    

    @rx.event 
    def set_selected_alignment(
        self, alignment: AlignmentOption
    ):
        self.selected_alignment = alignment

    @rx.event
    def toggle_explain(self):
        self.explain_active = not self.explain_active

    @rx.event
    def toggle_tasks(self):
        self.tasks_active = not self.tasks_active

    @rx.event
    async def handle_upload(
        self, files
    ):
        if not files:
            return
        file = files[0]
        upload_data = await file.read()
        
        # Upload file to FastAPI backend
        async with httpx.AsyncClient() as client:
            try:
                # Prepare the file for upload to FastAPI
                api_files = {'file': (file.filename, upload_data, file.content_type or 'application/octet-stream')}
                response = await client.post(
                    f"{FASTAPI_BASE_URL}/v1/upload_document", 
                    files=api_files, 
                    timeout=60.0
                )
                response.raise_for_status()
                
                # Get response data from FastAPI
                upload_response_data = response.json()
                
                self.uploaded_file_name = upload_response_data.get("filename", file.filename)
                print(f"File '{self.uploaded_file_name}' successfully uploaded to FastAPI backend.")
                
            except httpx.HTTPStatusError as e:
                error_detail = e.response.text
                try:
                    error_json = e.response.json()
                    if "detail" in error_json:
                        error_detail = error_json["detail"]
                except ValueError:
                    pass
                
                print(f"HTTP error uploading file to FastAPI: {e.response.status_code} - {error_detail}")
                self.uploaded_file_name = f"Error uploading {file.filename}: {error_detail}"
                return
                
            except httpx.RequestError as e:
                print(f"Network error uploading file to FastAPI: {str(e)}")
                self.uploaded_file_name = f"Network error uploading {file.filename}"
                return
                
            except Exception as e:
                print(f"Unexpected error uploading file to FastAPI: {e}")
                self.uploaded_file_name = f"Error uploading {file.filename}"
                return


    @rx.event
    def clear_uploaded_file(self):
        self.uploaded_file_name = ""
        # Clear uploaded file reference

    def _ensure_session_id(self):
        if not self.session_id:
            self.session_id = str(uuid.uuid4())

    @rx.event
    def clear_messages(self):
        self.messages = []
        self.processing = False
        self.input_message = ""
        # Reset VINO state
        self.session_id = None # Or decide on session persistence logic
        self.current_vino_step = 1
        self.current_planner_details = None
        # Reset new UI features state
        self.selected_alignment = "Guidance"
        self.explain_active = False
        self.tasks_active = False
        self.clear_uploaded_file() # Clears uploaded_file_name

    @rx.event
    def clear_input(self):
        """Clear the input message field"""
        self.input_message = ""

    @rx.event
    def force_clear_input(self):
        """Force clear the input message field with explicit refresh"""
        self.input_message = ""
        # Force a state update to ensure UI synchronization for both input areas
        return [
            rx.set_value("message-input", ""),
            rx.set_value("message-input-chat", "")
        ]

    @rx.event
    def set_input_message(self, value: str):
        """Set the input message field"""
        self.input_message = value

    @rx.event
    def handle_send_message(self):
        """Handle sending message - simplified without shift+enter functionality"""
        user_input = self.input_message.strip()
        if not user_input and not (self.explain_active or self.tasks_active or self.uploaded_file_name):
            return
        
        # If there's a pending step change proposal, and the user sends a new message,
        # we treat it as an implicit rejection.
        if self.proposed_next_step:
            print(f"Frontend: Implicitly clearing step change proposal to {self.proposed_next_step} due to new user message.")
            self.proposed_next_step = None
        
        # Clear input immediately for better UX
        self.input_message = ""
        
        # Send the message with the captured input
        return ChatState.send_message_with_text(user_input)

    @rx.event
    def send_message_with_text(self, user_text: str):
        """Send message with the provided text"""
        # Ensure input is cleared (double-check in case it wasn't cleared earlier)
        self.input_message = ""
        
        final_message_parts = []
        
        # File context is automatically retrieved by backend using uploaded_file_context_name
        if self.uploaded_file_name:
            final_message_parts.append(
                f"[File context: {self.uploaded_file_name}]"
            )
        
        # Backend handles explain_active and tasks_active flags automatically
        if self.explain_active:
            final_message_parts.append(
                "[Request: Explain conversation history]"
            )
        if self.tasks_active:
            final_message_parts.append(
                "[Request: Generate tasks based on conversation history]"
            )

        if user_text:
            if self.explain_active or self.tasks_active:
                final_message_parts.append(
                    f"[Focusing on: {user_text}]"
                )
            else:
                final_message_parts.append(user_text)
        
        full_user_message = " ".join(
            final_message_parts
        ).strip()

        if not full_user_message:
            # Allow sending if explain, tasks, or file is active even with empty input_message
            if not (
                self.explain_active
                or self.tasks_active
                or self.uploaded_file_name
            ):
                return

        if self.processing:
            return

        self._ensure_session_id()
        self.messages.append(
            {"text": full_user_message, "is_ai": False}
        )
        self.messages.append({"text": "", "is_ai": True}) # AI placeholder
        self.processing = True
        
        return ChatState.generate_response

    def _prepare_fastapi_history(self) -> List[Dict[str, Any]]:
        api_history = []
        for msg in self.messages[:-2]: # All messages except the last user input and AI placeholder
            role = "assistant" if msg["is_ai"] else "user"
            api_history.append({"role": role, "content": msg["text"]})
        return api_history

    @rx.event(background=True)
    async def generate_response(self):
        if not self.messages or not self.messages[-2]["text"].strip(): # Check the user message part
             # If the user message part is empty, but we have active flags or file, it's okay.
            if not (self.explain_active or self.tasks_active or self.uploaded_file_name):
                async with self:
                    if self.messages: # If there's an AI placeholder
                        self.messages[-1]["text"] = "Cannot send an empty message if no special actions (explain, tasks, file) are active."
                    self.processing = False
                return

        query_text = self.messages[-2]["text"] # The full user message constructed earlier
        api_history_payload = self._prepare_fastapi_history()
        
        payload = {
            "session_id": self.session_id,
            "query_text": query_text,
            "history": api_history_payload,
            "current_step": self.current_vino_step,  # Send the current frontend step to the backend
            "planner_details": self.current_planner_details,
            # FastAPI backend integration fields
            "selected_alignment": self.selected_alignment,
            "explain_active": self.explain_active,
            "tasks_active": self.tasks_active,
            "uploaded_file_context_name": self.uploaded_file_name if self.uploaded_file_name else None,
        }
        
        print(f"Frontend: Preparing request - current_step sent as: {payload['current_step']}")
        params = {"session_id": self.session_id}

        try:
            async with httpx.AsyncClient() as client:
                print(f"Frontend: Sending request with session_id: {self.session_id}")
                print(f"Frontend: Current frontend step before request: {self.current_vino_step}")
                response = await client.post(
                    f"{FASTAPI_BASE_URL}/v1/chat",
                    json=payload,
                    params=params,
                    timeout=120.0 # Increased timeout for potentially complex LLM calls
                )
                response.raise_for_status()
                response_data = response.json()
                print(f"Frontend: Received response with step: {response_data.get('current_step', 'NOT_PROVIDED')}")
                print(f"Frontend: Received response with proposed_next_step: {response_data.get('proposed_next_step', 'NOT_PROVIDED')}")


            async with self:
                self.messages[-1]["text"] = response_data.get("response", "No response text.")
                
                # New logic for two-stage step confirmation
                proposed_step = response_data.get("proposed_next_step")
                if proposed_step:
                    self.proposed_next_step = proposed_step
                    print(f"Frontend: Backend proposed step change to {proposed_step}. Awaiting confirmation.")
                else:
                    # If no new step is proposed, clear any existing proposal
                    if self.proposed_next_step:
                        print(f"Frontend: Clearing previous step proposal ({self.proposed_next_step}) as none was received in this response.")
                        self.proposed_next_step = None
                    
                self.current_planner_details = response_data.get("planner_details", self.current_planner_details)
                print(f"Frontend: Final frontend state - Step: {self.current_vino_step}, Proposed Step: {self.proposed_next_step}")
                
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_detail = error_json["detail"]
            except ValueError:
                pass 
            async with self:
                self.messages[-1]["text"] = f"Error communicating with VINO API: {e.response.status_code} - {error_detail}"
        except httpx.RequestError as e:
            async with self:
                self.messages[-1]["text"] = f"Network error calling VINO API: {str(e)}"
        except Exception as e:
            async with self:
                self.messages[-1]["text"] = f"An unexpected error occurred: {str(e)}"
        finally:
            async with self:
                self.processing = False
                # Reset one-time flags after processing, or manage their lifecycle as needed                # self.explain_active = False # Keep flags active for subsequent queries
                # self.tasks_active = False
                # If uploaded_file_name was for a single message context, clear it:
                # self.clear_uploaded_file() # Keep file context available for subsequent queries

    @rx.event
    def decline_step_change(self):
        """Decline the proposed step change."""
        if not self.proposed_next_step:
            return

        print(f"Frontend: User declined step change to {self.proposed_next_step}.")
        
        # Add a message to the chat to indicate rejection
        self.messages.append({
            "text": f"[Continuing on current step. Step change to {self.proposed_next_step} declined.]",
            "is_ai": False
        })
        
        self.proposed_next_step = None

    @rx.event(background=True)
    async def confirm_step_change(self):
        """Confirm the proposed step change and notify the backend."""
        if not self.proposed_next_step or self.confirmation_in_progress:
            return

        async with self:
            if not self.proposed_next_step: # Double check after acquiring lock
                return
            self.confirmation_in_progress = True
            self.processing = True
            
            confirmed_step = self.proposed_next_step
            
            # Add a message to the chat to indicate confirmation
            self.messages.append({
                "text": f"OK, let's move to step {confirmed_step}.",
                "is_ai": False
            })
            self.messages.append({"text": "", "is_ai": True}) # AI placeholder

            # Clear the proposal now that we are acting on it
            self.proposed_next_step = None

        # Prepare payload for backend
        payload = {
            "session_id": self.session_id,
            "query_text": f"User confirmed moving to step {confirmed_step}.",
            "history": self._prepare_fastapi_history(),
            "current_step": self.current_vino_step,
            "confirmed_next_step": confirmed_step,
            "planner_details": self.current_planner_details,
            "selected_alignment": self.selected_alignment,
            "explain_active": False,
            "tasks_active": False,
            "uploaded_file_context_name": None,
        }
        
        params = {"session_id": self.session_id}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{FASTAPI_BASE_URL}/v1/chat",
                    json=payload,
                    params=params,
                    timeout=120.0
                )
                response.raise_for_status()
                response_data = response.json()

            async with self:
                self.messages[-1]["text"] = response_data.get("response", "Step change confirmed.")
                
                old_step = self.current_vino_step
                
                current_step_from_backend = response_data.get("current_step", self.current_vino_step)
                if current_step_from_backend != self.current_vino_step:
                    self.current_vino_step = current_step_from_backend
                    print(f"Frontend: Step updated from {old_step} to {self.current_vino_step} after confirmation.")
                else:
                    print(f"Frontend: Step unchanged at {self.current_vino_step} even after confirmation.")
                
                self.current_planner_details = response_data.get("planner_details", self.current_planner_details)
                print(f"Frontend: Final frontend state - Step: {self.current_vino_step}")

            if old_step != self.current_vino_step:
                yield ChatState.force_navbar_refresh

        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_detail = error_json["detail"]
            except ValueError:
                pass 
            async with self:
                self.messages[-1]["text"] = f"Error confirming step change: {e.response.status_code} - {error_detail}"
        except httpx.RequestError as e:
            async with self:
                self.messages[-1]["text"] = f"Network error confirming step change: {str(e)}"
        except Exception as e:
            async with self:
                self.messages[-1]["text"] = f"An unexpected error occurred during step confirmation: {str(e)}"
        finally:
            async with self:
                self.processing = False
                self.confirmation_in_progress = False

    @rx.event
    def scroll_to_bottom(self):
        """This event handler is kept to prevent errors but does not perform any action."""