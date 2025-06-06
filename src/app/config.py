import os
from dotenv import load_dotenv
from pydantic import SecretStr

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')) # Adjust path to .env at project root

# --- PATHS ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) # c:\Users\Kuype\source\repos\vino-project
CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "chromadb")
DOCUMENTS_DIR = os.path.join(PROJECT_ROOT, "data", "framework_docs") # Assuming framework docs are in data/framework_docs
USER_UPLOADS_DIR = os.path.join(PROJECT_ROOT, "data", "user_uploads")

# --- DOCUMENT PROCESSING ---
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# --- CORS CONFIG ---
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Default Reflex frontend port
    "http://127.0.0.1:3000",
    # Add any other origins if needed
]

# --- API KEYS ---
raw_google_api_key = os.getenv("GOOGLE_API_KEY")
if not raw_google_api_key:
    raise ValueError("API key not found. Please set the GOOGLE_API_KEY environment variable.")
GOOGLE_API_KEY: SecretStr = SecretStr(raw_google_api_key) # Wrap the key in SecretStr

# --- LLM ---
LLM_MODEL_NAME = "gemini-1.5-pro"
LLM_TEMPERATURE = 0
LLM_MAX_TOKENS = None
LLM_TIMEOUT = None
LLM_MAX_RETRIES = 2

# --- VECTOR DB ---
FRAMEWORKS_COLLECTION_NAME = "frameworks"
USER_DOCUMENTS_COLLECTION_NAME = "user_documents"

# ChromaDB Configuration
CHROMA_SERVER_HOST = os.getenv("CHROMA_SERVER_HOST", "localhost")
CHROMA_SERVER_PORT = int(os.getenv("CHROMA_SERVER_PORT", "8001"))  # Default to 8001 for local dev, 8000 in Docker
CHROMA_SERVER_URL = f"http://{CHROMA_SERVER_HOST}:{CHROMA_SERVER_PORT}"

# Use Docker-based ChromaDB or local persistent client
USE_CHROMA_SERVER = os.getenv("USE_CHROMA_SERVER", "false").lower() == "true"

# Ensure upload directory exists
os.makedirs(USER_UPLOADS_DIR, exist_ok=True)
os.makedirs(CHROMA_DB_PATH, exist_ok=True)
# Ensure framework documents directory exists (optional, can be created manually)
# os.makedirs(DOCUMENTS_DIR, exist_ok=True)

