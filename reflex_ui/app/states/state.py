import reflex as rx
import httpx

BACKEND_API_URL = "http://127.0.0.1:8000"
# ---------------------------------
## TODO put this into chat_state or db_state?
class State(rx.State):
    """The app state."""
    # Maximum number of entries to keep in chat history
    MAX_HISTORY_LENGTH = 10

    # The current question being asked.
    question: str = ""  # Initialize with an empty string

    # Keep track of the chat history as a list of (question, answer) tuples.
    chat_history: list[tuple[str, str]] = []

    # Track the current step in the Universal Matrix
    current_step: int = 1

    is_loading: bool = False
    error_message: str = ""

    def set_question(self, question: str):
        """Set the current question text."""
        self.question = question

    @rx.event
    def clear_chat_history(self):
        """Clear the chat history, error messages, and reset step."""
        self.chat_history = []
        self.error_message = ""
        self.current_step = 1 # Reset step on clear

    @rx.event
    async def answer(self):
        """Process the current question, handle /next command, or get an answer from the backend API."""
        # Skip empty questions
        if not self.question or not self.question.strip():
            print("❓ Question is empty, skipping.")
            return

        # --- Handle /next command ---
        if self.question.strip().lower() == "/next":
            if self.current_step < 6:
                self.current_step += 1
                feedback_message = f"➡️ Moved to Step {self.current_step}."
                print(f"⚙️ {feedback_message}")
                # Add feedback to chat history (optional, but helpful for user)
                self.chat_history.append(("/next", feedback_message))
            else:
                feedback_message = "✅ You are already at the final step (Step 6)."
                print(f"⚙️ {feedback_message}")
                self.chat_history.append(("/next", feedback_message))

            self.question = "" # Clear input field
            self.error_message = "" # Clear any previous errors
            yield # Update UI
            return # Stop processing, don't call backend for /next

        # --- Process regular question ---
        # Start loading state
        self.is_loading = True
        self.error_message = ""
        yield  # Update UI to show loading state

        # Prepare question and add placeholder in chat history
        question_to_send = self.question
        self.chat_history.append((question_to_send, "..."))
        self.question = ""  # Clear input field
        yield  # Update UI with placeholder

        # --- Prepare history for backend ---
        history_for_backend = []
        for q, a in self.chat_history[:-1]: # Exclude the placeholder
             # Skip adding command feedback to the actual LLM history
            if q.strip().lower() != "/next":
                history_for_backend.append({"role": "user", "content": q})
                history_for_backend.append({"role": "assistant", "content": a})

        try:
            # Call backend API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BACKEND_API_URL}/chat",
                    json={
                        "question": question_to_send,
                        "history": history_for_backend,
                        "current_step": self.current_step # <-- Pass the current step
                    },
                    timeout=30.0
                )
                response.raise_for_status()

                # Process response
                response_data = response.json()
                backend_answer = response_data.get("answer", "Error: No answer received.")

                # Update chat history with actual response
                self.chat_history[-1] = (question_to_send, backend_answer)

        except httpx.HTTPStatusError as e:
            # Handle HTTP errors (e.g., 404, 500) from backend
            error_detail = "Unknown error"
            try:
                error_detail = e.response.json().get("detail", e.response.text)
            except Exception: # Handle cases where response is not JSON
                 error_detail = e.response.text
            print(f"🔴 HTTP error calling backend: {e.response.status_code} - {error_detail}")
            self.error_message = f"Error: {error_detail}"
            self.chat_history[-1] = (
                question_to_send,
                f"Error: Failed to get response ({e.response.status_code})"
            )
        except httpx.RequestError as e:
            # Handle network errors (e.g., connection refused)
            print(f"🔴 Network error calling backend: {e}")
            self.error_message = "Error: Could not connect to the backend service."
            self.chat_history[-1] = (question_to_send, "Error: Connection failed.")
        except Exception as e:
            # Handle other unexpected errors
            print(f"🔴 Unexpected error in answer handler: {e}")
            self.error_message = "An unexpected error occurred."
            self.chat_history[-1] = (question_to_send, "Error: An unexpected error occurred.")
        finally:
            # Stop loading indicator regardless of success or failure
            self.is_loading = False
            yield  # Update UI

    # --- File Upload Handler ---
    async def handle_upload(self, files: list[rx.UploadFile]):
        """Handle files uploaded via rx.upload."""
        self.is_loading = True  # Show loading indicator
        self.error_message = ""
        yield

        upload_results = []
        async with httpx.AsyncClient() as client:
            for file in files:
                try:
                    # Read file content provided by Reflex
                    file_content = await file.read()

                    # Send file to backend /upload endpoint
                    response = await client.post(
                        f"{BACKEND_API_URL}/upload",
                        files={"file": (file.filename, file_content, file.content_type)},
                        timeout=60.0  # Allow more time for uploads
                    )
                    response.raise_for_status()

                    # Add success message (you could display this in the UI)
                    result_detail = response.json().get("detail", f"Uploaded {file.filename}")
                    upload_results.append(result_detail)
                    print(f"✅ {result_detail}")

                except httpx.HTTPStatusError as e:
                    error_detail = "Unknown error"
                    try:
                        error_detail = e.response.json().get("detail", e.response.text)
                    except Exception:
                        error_detail = e.response.text
                    print(f"🔴 HTTP error uploading {file.filename}: {e.response.status_code} - {error_detail}")
                    self.error_message = f"Error uploading {file.filename}: {error_detail}"
                    upload_results.append(f"Error uploading {file.filename}")
                    # Optionally break or continue on error
                except Exception as e:
                    print(f"🔴 Error processing upload {file.filename}: {e}")
                    self.error_message = f"Error uploading {file.filename}."
                    upload_results.append(f"Error uploading {file.filename}")

        self.is_loading = False
        # Optionally update UI with upload_results details
        # Example: self.chat_history.append(("System", f"Upload results: {', '.join(upload_results)}"))
        yield
