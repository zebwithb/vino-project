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
    uploaded_file_name: str = "" # Name of the file displayed in UI
    # TODO LOOSE END 3.2: Consider if a separate internal reference to the uploaded file is needed for the API
    # e.g., a file ID returned by the FastAPI upload endpoint. For now, we'll pass the filename.
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
        
        # TODO LOOSE END 3.1: Implement actual file upload to FastAPI backend
        # The following lines save locally, which is good for rx.UploadFile,
        # but the data needs to be sent to FastAPI's /v1/upload_document
        # For now, we'll just set the filename for UI display.
        # Example of how you might upload to FastAPI:
        # async with httpx.AsyncClient() as client:
        #     try:
        #         api_files = {'file': (file.name, upload_data, file.content_type)}
        #         response = await client.post(f"{FASTAPI_BASE_URL}/v1/upload_document", files=api_files, timeout=60.0)
        #         response.raise_for_status()
        #         # Assuming FastAPI returns info about the uploaded file, e.g., its server-side filename or ID
        #         # upload_response_data = response.json()
        #         async with self:
        #             self.uploaded_file_name = file.name # Or use filename from response
        #             # self.uploaded_file_reference_for_api = upload_response_data.get("server_filename_or_id")
        #     except Exception as e:
        #         print(f"Error uploading file to FastAPI: {e}") # Handle error appropriately in UI
        #         async with self:
        #             self.uploaded_file_name = f"Error uploading {file.name}" # Indicate error in UI
        #         return

        # For now, just setting the name for UI and assuming backend handles it by name later
        async with self:
            self.uploaded_file_name = file.name
            print(f"File '{file.name}' selected. TODO: Implement upload to FastAPI backend.")


    @rx.event
    def clear_uploaded_file(self):
        self.uploaded_file_name = ""
        # TODO LOOSE END 3.3: If you store a separate API reference for the file, clear it too.

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
        final_message_parts = []

        # TODO LOOSE END 3.4: How the uploaded file context is used by the backend needs to be defined.
        # For now, we just indicate its presence in the user message.
        # The backend might need to know to retrieve this file's content based on `self.uploaded_file_name`.
        if self.uploaded_file_name:
            final_message_parts.append(
                f"[File context: {self.uploaded_file_name}]"
            )

        # TODO LOOSE END 2.1: How `explain_active` and `tasks_active` translate to backend actions.
        # The backend will receive these flags.
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
        # self.uploaded_file_name = "" # Clear after sending message, or manage lifecycle differently
        # TODO LOOSE END 3.5: Decide when to clear `uploaded_file_name`.
        # Clearing it here means it's only for one message. If it should persist, don't clear.
        # For now, let's assume it's cleared after being included in a message.
        # self.clear_uploaded_file() # This might be too soon if the backend needs it for context over multiple turns.
        # Let's keep it until explicitly cleared by user or new upload.

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
            "query_text": query_text,
            "history": api_history_payload,
            "current_step": self.current_vino_step,
            "planner_details": self.current_planner_details,
            # --- New fields for FastAPI to handle ---
            # TODO LOOSE END 1.1: FastAPI backend needs to be updated to accept and use 'selected_alignment'.
            "selected_alignment": self.selected_alignment,
            # TODO LOOSE END 2.2: FastAPI backend needs to be updated to accept and use these flags.
            "explain_active": self.explain_active,
            "tasks_active": self.tasks_active,
            # TODO LOOSE END 3.6: FastAPI backend needs to be updated to accept 'uploaded_file_name'
            # and use it to retrieve context from a previously uploaded file.
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
                # TODO LOOSE END 4: Consider if FastAPI should return new states for explain_active/tasks_active
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
                # Reset one-time flags after processing, or manage their lifecycle as needed
                # self.explain_active = False # TODO LOOSE END 2.3: Decide if these flags reset automatically
                # self.tasks_active = False
                # If uploaded_file_name was for a single message context, clear it:
                # self.clear_uploaded_file() # TODO LOOSE END 3.7: Re-evaluate when to clear uploaded_file_name