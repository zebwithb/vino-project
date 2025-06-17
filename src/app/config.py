import os
import re
from dotenv import load_dotenv
from pydantic import SecretStr

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')) # Adjust path to .env at project root

# --- PATHS ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) # c:\Users\Kuype\source\repos\vino-project
CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "chromadb")
DOCUMENTS_DIR = os.path.join(PROJECT_ROOT, "data", "framework_docs") # Assuming framework docs are in data/framework_docs
USER_UPLOADS_DIR = os.path.join(PROJECT_ROOT, "data", "user_uploads")
NEW_DOCUMENTS_DIR = os.path.join(PROJECT_ROOT, "kb_new")
KB_DOCUMENTS_DIR = os.path.join(PROJECT_ROOT, "kb")
NEW_USER_UPLOADS_DIR = os.path.join(PROJECT_ROOT, "new_user_uploads")
# --- SERVICES ---
# Configuration constants
DEBUG_MODE = False  # Set to True to enable debug output
DEFAULT_MAX_KEYWORDS = 5
DEFAULT_ABSTRACT_LENGTH = 300
SUPPORTED_EXTENSIONS = ['.md', '.docx', '.pdf']

# Common English stopwords for keyword extraction
STOPWORDS = {
    'and', 'the', 'is', 'in', 'to', 'of', 'for', 'with', 'on', 'at', 'from',
    'by', 'about', 'as', 'it', 'this', 'that', 'be', 'are', 'was', 'were',
    'an', 'or', 'but', 'if', 'then', 'because', 'when', 'where', 'why', 'how'
}

# --- CHUNKING ---
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
# Environment settings
DEBUG_MODE = os.getenv('CHUNKING_DEBUG', 'TRUE').lower() == 'true'

# Directory settings

ROOT_DIR = os.getenv('CHUNKING_ROOT_DIR', 'kb_new')
UPLOAD_DIR = os.getenv('CHUNKING_UPLOAD_DIR', 'new_user_uploads')

# File processing settings
ALLOWED_FILETYPES = ['.md', '.docx', '.pdf', '.txt']
MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '50'))

# Chunking settings
MAX_CHUNK_TOKENS = int(os.getenv('MAX_CHUNK_TOKENS', '300'))  # Increased from 300 to 800 tokens
MIN_CHUNK_TOKENS = int(os.getenv('MIN_CHUNK_TOKENS', '50'))   # Increased from 50 to 100 tokens
OVERLAP_TOKENS = int(os.getenv('OVERLAP_TOKENS', '80'))        # Increased from 20 to 80 tokens

# Text processing settings
REMOVE_ARTIFACTS = ['[image]', '[]', '[figure]', '[table]']
PRESERVE_FORMATTING = ['```', '`', '**', '*', '__', '_']

# Model settings
ENCODING_MODEL = os.getenv('ENCODING_MODEL', 'gpt-3.5-turbo')
TOKEN_ESTIMATION_RATIO = float(os.getenv('TOKEN_ESTIMATION_RATIO', '0.75'))

# Output settings
CHUNK_SEPARATOR = ' [SEP] '
DEFAULT_SECTION_NAME = 'Full Document'

# Compiled regex patterns for better performance
# Updated to detect both dash-based TOCs and dot-based TOCs (common in PDFs)
TOC_PATTERN = re.compile(r'(- .*\r?\n\r?\n[A-Z]|\.{3,}.*\d+\s*\n)')
# Pattern to detect dot-based table of contents entries
DOT_TOC_PATTERN = re.compile(r'^[^.\n]+\.{3,}.*\d+\s*$', re.MULTILINE)
# Pattern to detect the end of TOC and start of content
TOC_END_PATTERN = re.compile(r'\n\s*\n\s*([A-Z][a-z]+|\w+\s+[A-Z])')
LINE_ENDING_PATTERN = re.compile(r'\r\n|\r')
PARAGRAPH_BREAK_PATTERN = re.compile(r'\n{2,}')
WHITESPACE_PATTERN = re.compile(r'(?<!\n) +')
NEWLINE_REPLACE_PATTERN = re.compile(r'(?<!\n)\n(?!(\n|- ))')
BULLET_NUMBERED_PATTERN = re.compile(r'\n- |\n\d+\.')
SENTENCE_SPLIT_PATTERN = re.compile(r'(?<=[.!?])\s+')
LINES_PER_PAGE = 40  # Estimate for text files

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


