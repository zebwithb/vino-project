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

    @rx.event(background=True) # Keep background=True for file operations
    async def handle_upload(
        self, files: list[rx.UploadFile]
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
                    f"{FASTAPI_BASE_URL}/upload_document", 
                    files=api_files, 
                    timeout=60.0
                )
                response.raise_for_status()
                
                # Get response data from FastAPI
                upload_response_data = response.json()
                
                async with self:
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
                async with self:
                    self.uploaded_file_name = f"Error uploading {file.filename}: {error_detail}"
                return
                
            except httpx.RequestError as e:
                print(f"Network error uploading file to FastAPI: {str(e)}")
                async with self:
                    self.uploaded_file_name = f"Network error uploading {file.filename}"
                return
                
            except Exception as e:
                print(f"Unexpected error uploading file to FastAPI: {e}")
                async with self:
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
    def send_message_from_input(self):
        user_text = self.input_message.strip()
        final_message_parts = []        # File context is automatically retrieved by backend using uploaded_file_context_name
        if self.uploaded_file_name:
            final_message_parts.append(
                f"[File context: {self.uploaded_file_name}]"
            )        # Backend handles explain_active and tasks_active flags automatically
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
        self.input_message = ""
        # self.uploaded_file_name = "" # Clear after sending message, or manage lifecycle differently        # Keep uploaded file available for subsequent queries until manually cleared

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
            "current_step": self.current_vino_step,
            "planner_details": self.current_planner_details,
            # FastAPI backend integration fields
            "selected_alignment": self.selected_alignment,
            "explain_active": self.explain_active,
            "tasks_active": self.tasks_active,
            "uploaded_file_context_name": self.uploaded_file_name if self.uploaded_file_name else None,
        }
        
        params = {"session_id": self.session_id}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{FASTAPI_BASE_URL}/v1/chat",
                    json=payload,
                    params=params,
                    timeout=120.0 # Increased timeout for potentially complex LLM calls
                )
                response.raise_for_status()
                response_data = response.json()

            async with self:
                self.messages[-1]["text"] = response_data.get("response", "No response text.")
                self.current_vino_step = response_data.get("current_step", self.current_vino_step)
                self.current_planner_details = response_data.get("planner_details", self.current_planner_details)
                # Backend response processed successfully
                # For example, if a task generation completes, tasks_active might be set to False by the backend.
                # self.explain_active = response_data.get("explain_active_status", self.explain_active)
                # self.tasks_active = response_data.get("tasks_active_status", self.tasks_active)

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