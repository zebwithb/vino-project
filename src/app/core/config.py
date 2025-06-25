import os
import re
from dotenv import load_dotenv
from pydantic import SecretStr

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env'))

class Settings:
    def __init__(self):
        # --- PROJECT INFO ---
        self.PROJECT_NAME = "VINO API"
        self.PROJECT_DESCRIPTION = "VINO API for inference, document processing and vector database management"
        self.VERSION = "1.3.0"
        
        # --- PATHS ---
        self.PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.CHROMA_DB_PATH = os.path.join(self.PROJECT_ROOT, "chromadb")
        self.DOCUMENTS_DIR = os.path.join(self.PROJECT_ROOT, "data", "framework_docs")
        self.USER_UPLOADS_DIR = os.path.join(self.PROJECT_ROOT, "data", "user_uploads")
        self.NEW_DOCUMENTS_DIR = os.path.join(self.PROJECT_ROOT, "data", "kb_new")
        self.KB_DOCUMENTS_DIR = os.path.join(self.PROJECT_ROOT, "data", "kb")
        self.NEW_USER_UPLOADS_DIR = os.path.join(self.PROJECT_ROOT, "data", "new_user_uploads")
          # --- API KEYS ---
        raw_google_api_key = os.getenv("GOOGLE_API_KEY")
        if not raw_google_api_key:
            raise ValueError("API key not found. Please set the GOOGLE_API_KEY environment variable.")
        self.GOOGLE_API_KEY: SecretStr = SecretStr(raw_google_api_key)
        
        # --- SUPABASE CONFIG ---
        self.SUPABASE_URL = os.getenv("SUPABASE_URL", "")
        self.SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
        
        # --- LLM CONFIG ---
        self.LLM_MODEL_NAME = "gemini-1.5-flash"
        self.LLM_TEMPERATURE = 0
        self.LLM_MAX_TOKENS = None
        self.LLM_TIMEOUT = None
        self.LLM_MAX_RETRIES = 2
        
        # --- VECTOR DB ---
        self.FRAMEWORKS_COLLECTION_NAME = "frameworks"
        self.USER_DOCUMENTS_COLLECTION_NAME = "user_documents"
        self.CHROMA_SERVER_HOST = os.getenv("CHROMA_SERVER_HOST", "localhost")
        self.CHROMA_SERVER_PORT = int(os.getenv("CHROMA_SERVER_PORT", "8001"))
        self.CHROMA_SERVER_URL = f"http://{self.CHROMA_SERVER_HOST}:{self.CHROMA_SERVER_PORT}"
        self.USE_CHROMA_SERVER = os.getenv("USE_CHROMA_SERVER", "false").lower() == "true"
        
        # --- DOCUMENT PROCESSING ---
        self.DEBUG_MODE = os.getenv('CHUNKING_DEBUG', 'FALSE').lower() == 'true'
        self.DEFAULT_MAX_KEYWORDS = 5
        self.DEFAULT_ABSTRACT_LENGTH = 300
        self.SUPPORTED_EXTENSIONS = ['.md', '.docx', '.pdf', '.txt']
        self.ALLOWED_FILETYPES = ['.md', '.docx', '.pdf', '.txt']
        self.MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '50'))
        
        # --- CHUNKING SETTINGS ---
        self.CHUNK_SIZE = 1000
        self.CHUNK_OVERLAP = 200
        self.MAX_CHUNK_TOKENS = int(os.getenv('MAX_CHUNK_TOKENS', '300'))
        self.MIN_CHUNK_TOKENS = int(os.getenv('MIN_CHUNK_TOKENS', '50'))
        self.OVERLAP_TOKENS = int(os.getenv('OVERLAP_TOKENS', '80'))
        
        # --- TEXT PROCESSING ---
        self.REMOVE_ARTIFACTS = ['[image]', '[]', '[figure]', '[table]']
        self.PRESERVE_FORMATTING = ['```', '`', '**', '*', '__', '_']
        self.ENCODING_MODEL = os.getenv('ENCODING_MODEL', 'gpt-3.5-turbo')
        self.TOKEN_ESTIMATION_RATIO = float(os.getenv('TOKEN_ESTIMATION_RATIO', '0.75'))
        self.CHUNK_SEPARATOR = ' [SEP] '
        self.DEFAULT_SECTION_NAME = 'Full Document'
        self.LINES_PER_PAGE = 40
        
        # --- STOPWORDS ---
        self.STOPWORDS = {
            'and', 'the', 'is', 'in', 'to', 'of', 'for', 'with', 'on', 'at', 'from',
            'by', 'about', 'as', 'it', 'this', 'that', 'be', 'are', 'was', 'were',
            'an', 'or', 'but', 'if', 'then', 'because', 'when', 'where', 'why', 'how'
        }
        
        # --- REGEX PATTERNS ---
        self.TOC_PATTERN = re.compile(r'(- .*\r?\n\r?\n[A-Z]|\.{3,}.*\d+\s*\n)')
        self.DOT_TOC_PATTERN = re.compile(r'^[^.\n]+\.{3,}.*\d+\s*$', re.MULTILINE)
        self.TOC_END_PATTERN = re.compile(r'\n\s*\n\s*([A-Z][a-z]+|\w+\s+[A-Z])')
        self.LINE_ENDING_PATTERN = re.compile(r'\r\n|\r')
        self.PARAGRAPH_BREAK_PATTERN = re.compile(r'\n{2,}')
        self.WHITESPACE_PATTERN = re.compile(r'(?<!\n) +')
        self.NEWLINE_REPLACE_PATTERN = re.compile(r'(?<!\n)\n(?!(\n|- ))')
        self.BULLET_NUMBERED_PATTERN = re.compile(r'\n- |\n\d+\.')
        self.SENTENCE_SPLIT_PATTERN = re.compile(r'(?<=[.!?])\s+')
        
        # --- CORS CONFIG ---
        self.CORS_ALLOWED_ORIGINS = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
        
        # Ensure required directories exist
        os.makedirs(self.USER_UPLOADS_DIR, exist_ok=True)
        os.makedirs(self.CHROMA_DB_PATH, exist_ok=True)

settings = Settings()