from fastapi import APIRouter, HTTPException, UploadFile, File
import shutil
import os

router = APIRouter(prefix="/v1", tags=["documents"])

# Define a directory to store uploaded files
# TODO Ensure this path is correct and writable by your FastAPI application
UPLOAD_DIRECTORY = "./uploaded_files_context" # Or a more absolute/configurable path
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

@router.post("/upload_document")
async def upload_document(file: UploadFile = File(...)):
    """
    Receives a file, saves it to the UPLOAD_DIRECTORY.
    This endpoint is used by the Reflex frontend to upload files
    that can later be used as context in the chat.
    """
    try:
        # It's crucial that the file is saved in a way that the /v1/chat endpoint
        # can retrieve it later using the 'uploaded_file_context_name' (which will be file.filename).
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename cannot be None.")
        file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)
        
        # Basic security check: sanitize filename to prevent path traversal
        # For production, more robust validation/sanitization is needed.
        if ".." in file.filename or file.filename.startswith("/"):
            raise HTTPException(status_code=400, detail="Invalid filename.")

        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
        
        # The Reflex frontend's ChatState.handle_upload uses file.name (client-side)
        # to set `self.uploaded_file_name`. This endpoint's response confirms the action.
        # The /v1/chat endpoint will later use this filename to find the file.
        return {"filename": file.filename, "message": "File uploaded successfully and ready for context."}
    except HTTPException:
        raise # Re-raise HTTPException to ensure correct status code and detail
    except Exception as e:
        # Log the exception e for debugging
        raise HTTPException(status_code=500, detail=f"Could not upload file: {str(e)}")

# You might also want an endpoint to check file status or retrieve file content directly,
# though for the chat, it seems the /v1/chat endpoint will handle context retrieval.