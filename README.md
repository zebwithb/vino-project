# VINO AI - Production-Ready FastAPI Document Processing & Chat System

A production-ready FastAPI-based intelligent document processing and chat application that combines ChromaDB vector database with Google's Generative AI for semantic search, document context-aware conversations, and scalable session management.

##  Development Phases Overview

This project was developed through four major phases to achieve production readiness:

### **Phase 1: Foundation & Configuration Management**

- ✅ Centralized configuration management with `Settings` class
- ✅ Dependency injection architecture
- ✅ Service separation and clean interfaces
- ✅ CORS configuration and security basics

### **Phase 2: Service Purification & Ingestion Pipeline**

- ✅ Microservice-style architecture with pure service responsibilities
- ✅ Document ingestion pipeline with orchestration
- ✅ File system service for storage management
- ✅ Comprehensive error handling and validation

### **Phase 3: Document Context in Chat**

- ✅ Context-aware chat with file-specific conversations
- ✅ Advanced prompt engineering with document context
- ✅ Router-based endpoint organization
- ✅ Enhanced request/response models

### **Phase 4: Production Session Management**

- ✅ Persistent session storage using Redis with optional Supabase backend
- ✅ Stateless application design for horizontal scaling
- ✅ Session lifecycle management and cleanup
- ✅ Admin endpoints for session monitoring

### **Phase 5: UI/UX Focus**

These features are to be implemented, reviewed and depent on future decisions.

- Dynamic Context Switching
- Knowledge Base Architecture for Context Management
- Summarization techniques for different levels of Abstraction in Text
- UM Graph Overview, or other overview methods for better context management
- User Friendly features like file management and organization interfaces
- Local LLM Inference endpoint support

## Features

### **Core Capabilities**

- **Intelligent Document Processing**: Advanced PDF and text processing with semantic chunking
- **Context-Aware Chat**: File-specific conversations with document context injection
- **Semantic Search**: Vector-based similarity search using Google Generative AI embeddings
- **Persistent Sessions**: Scalable session management with Redis and optional Supabase storage
- **Admin Dashboard**: Session monitoring, cleanup, and management endpoints

### **Production Features**

- **Horizontal Scalability**: Stateless design supports multiple app instances
- **Graceful Degradation**: Fallback mechanisms for service reliability
- **Health Monitoring**: Comprehensive health checks and status endpoints
- **Security**: CORS configuration, input validation, and secure secrets management
- **Dependency Injection**: Clean, testable, and maintainable service architecture

## Architecture

### **High-Level Architecture**

```text
┌─────────────────┬─────────────────┬─────────────────┐
│   Presentation  │    Business     │      Data       │
│     Layer       │     Logic       │     Layer       │
├─────────────────┼─────────────────┼─────────────────┤
│ FastAPI Routes  │ Service Layer   │ Vector Database │
│ - Chat Router   │ - ChatService   │ - ChromaDB      │
│ - Admin Routes  │ - IngestionSvc  │ - Supabase      │
│ - Health Checks │ - VectorDBSvc   │ - File System   │
│                 │ - SessionSvc    │                 │
└─────────────────┴─────────────────┴─────────────────┘
```

Presentation layer is reflected in the Reflex UI, endpoints can be checked through /docs endpoint.

### **Service Dependencies**

```text
ChatService
├── VectorDBService (document retrieval)
├── SessionStorageService (persistent state)
└── PromptBuilder (context injection)

IngestionService (orchestrator)
├── DocumentService (processing)
├── VectorDBService (storage)
├── FileSystemService (file ops)
└── MetadataService (tracking)

SessionStorageService
├── SupabaseService (optional persistent storage)
└── Redis (caching and session storage)
```

### **Technology Stack**

- **Backend**: FastAPI with async/await support
- **AI/ML**: Google Generative AI (Gemini) for embeddings and chat
- **Vector DB**: ChromaDB for semantic search and document storage (embedded)
- **Session Storage**: Redis for caching with optional Supabase PostgreSQL for persistence
- **File Processing**: PyPDF2, python-docx for document parsing
- **Validation**: Pydantic for request/response validation
- **DI Container**: Custom dependency injection system

## 📁 Project Structure

```text
vino-project/
├── .github/                          # GitHub Actions workflows
│   └── workflows/
│       └── ci.yml                   # CI/CD pipeline configuration
├── src/app/                         # FastAPI backend application
│   ├── core/
│   │   ├── config.py                # Centralized configuration management
│   │   └── exceptions.py            # Custom exception classes
│   ├── dependencies.py             # Dependency injection providers
│   ├── main.py                     # FastAPI application with DI & routers
│   ├── endpoints/                  # API route handlers
│   │   ├── chat.py                 # Chat router with context support
│   │   ├── file_handler.py         # File upload/management endpoints
│   │   └── health.py               # Health check endpoints
│   ├── services/                   # Business logic layer
│   │   ├── chat_service.py         # Context-aware chat with sessions
│   │   ├── chunking_service.py     # Document chunking logic
│   │   ├── document_service.py     # Document parsing utilities
│   │   ├── extraction_service.py   # Text extraction from files
│   │   ├── file_system_service.py  # File operations & storage
│   │   ├── ingestion_pipeline_service.py # Document processing pipeline
│   │   ├── session_storage_service.py # Persistent session management
│   │   ├── supabase_service.py     # Supabase client service
│   │   └── vector_db_service.py    # ChromaDB operations
│   ├── schemas/
│   │   └── models.py               # Pydantic request/response models
│   └── prompt_engineering/         # AI prompt management
│       ├── builder.py              # Context-aware prompt building
│       ├── templates.py            # Prompt templates
│       └── matrix_definitions.py   # Universal matrix definitions
├── reflex_ui/                      # Reflex frontend application
│   ├── app/                        # Reflex app components
│   │   ├── components/             # UI components
│   │   │   ├── chat_interface.py   # Chat interface component
│   │   │   ├── input_area.py       # Input area component
│   │   │   ├── message_bubble.py   # Message bubble component
│   │   │   ├── navbar.py           # Navigation bar
│   │   │   └── typing_indicator.py # Typing indicator
│   │   ├── states/                 # State management
│   │   │   ├── chat_state.py       # Chat state logic
│   │   │   └── state.py            # Global state
│   │   └── app.py                  # Main Reflex app
│   ├── assets/                     # Static assets (images, icons)
│   ├── uploaded_files/             # User uploaded files storage
│   ├── requirements.txt            # Reflex dependencies
│   ├── rxconfig.py                 # Reflex configuration
│   └── style.py                    # Styling definitions
├── tests/                          # Comprehensive test suite (WIP)
│   ├── test_app.py                 # Application tests
│   ├── test_phase3.py              # Context & chat tests
│   ├── test_phase4.py              # Session storage tests
│   └── test_phase3_integration.py  # Integration tests
├── database/
│   └── migrations/                 # Database migration scripts
│       └── 001_create_chat_sessions.py
├── data/                           # Application data
│   ├── chroma/                     # ChromaDB storage
│   ├── framework_docs/             # Pre-loaded documentation
│   └── user_uploads/               # User-uploaded documents
├── docs/                           # Project documentation
│   ├── architecture/               # System design documents
│   ├── learning/                   # Research and iterations
│   ├── process/                    # Development process docs
│   ├── ci-cd-architecture.md       # CI/CD documentation
│   ├── error-handling-architecture.md # Error handling guide
│   └── phase3_implementation.md    # Phase 3 implementation details
├── documents/                      # Sample documents for testing
├── docker-compose.yml              # Main Docker services configuration
├── docker-compose.ci.yml           # CI-specific Docker configuration
├── Dockerfile.fastapi              # FastAPI service container
├── Dockerfile.reflex               # Reflex service container
├── pyproject.toml                  # Project configuration & dependencies
├── requirements.txt                # Auto-generated by uv (for compatibility)
├── rxconfig.py                     # Global Reflex configuration
├── uv.lock                         # UV package lock file
└── test_phase3_integration.py      # Integration test runner
```

## Quick Start

### Prerequisites

- Python 3.8+
- Google Generative AI API key
- Supabase account (for persistent sessions)
- Docker (optional, for ChromaDB server mode)

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd vino-project
   ```

2. **Install uv**

[uv Installation Methods](https://docs.astral.sh/uv/getting-started/installation/#installation-methods)

Follow the installation steps depending on your OS.
Make sure the ENVIRONMENT VARIABLES are set up correctly for terminal/CLI use.

1. **Install dependencies**

   ```bash
   uv sync --all-extras
   ```

2. **Set up environment variables**

   Create a `.env` file in the project root:

   ```env
   # Required: Google AI API Key
   GOOGLE_API_KEY=your_google_api_key_here
   
   # Required: Supabase Configuration (for persistent sessions)
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your_supabase_anon_key
   
   # Optional: ChromaDB Configuration
   USE_CHROMA_SERVER=false
   CHROMA_SERVER_HOST=localhost
   CHROMA_SERVER_PORT=8001
   
   # Optional: Chunking Debug Mode
   CHUNKING_DEBUG=false
   ```

3. **Set up Supabase Database (OPTIONAL)**

   Run the session storage migration in your Supabase SQL editor:

   ```sql
   CREATE TABLE IF NOT EXISTS chat_sessions (
       id SERIAL PRIMARY KEY,
       session_id VARCHAR(255) UNIQUE NOT NULL,
       conversation_history JSONB DEFAULT '[]'::jsonb,
       current_step INTEGER DEFAULT 1,
       planner_details TEXT,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
       updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
       last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );
   
   CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_id ON chat_sessions(session_id);
   CREATE INDEX IF NOT EXISTS idx_chat_sessions_last_accessed ON chat_sessions(last_accessed);
   ```

### Running the Application

#### Local Mode (Default)

Because of current port configuration it is important to run FastAPI first, and Reflex second, Reflex will dynamically adjust to an available port.
The default port of FastAPI is 8000.

```bash
# Start the FastAPI application
cd ./src
uv run fastapi dev
# Access the API at http://localhost:8000
# View API docs at http://localhost:8000/docs
```

```bash
# Start the Reflex Web App
cd ./reflex_ui
uv run reflex run --env dev

```

#### Docker Mode

See the [🐳 Docker Deployment](#-docker-deployment) section above for complete Docker setup instructions.

## 📡 API Endpoints

### **Chat & Conversation**

#### `POST /v1/chat`

Context-aware chat with optional file-specific conversations.

**Request Body:**

```json
{
  "message": "What are the key principles in this document?",
  "session_id": "optional-session-id",
  "uploaded_file_context_name": "document.pdf",
  "mode": "chat"
}
```

**Response:**

```json
{
  "response": "Based on the document context...",
  "session_id": "generated-or-provided-session-id",
  "current_step": 2,
  "context_sources": ["document.pdf"]
}
```

### **Document Management**

#### `POST /v1/upload`

Upload and process documents for semantic search.

**Request:**

- Multipart form with `file` field
- Optional `collection` parameter

**Response:**

```json
{
  "message": "File uploaded successfully",
  "filename": "document.pdf",
  "collection": "user_documents"
}
```

#### `GET /v1/files`

List uploaded files and collections.

#### `POST /v1/query`

Semantic search across document collections.

**Request Body:**

```json
{
  "query": "machine learning concepts",
  "collection": "user_documents",
  "max_results": 5
}
```

### **Admin & Session Management**

#### `GET /v1/admin/session/{session_id}`

Get session information and metadata.

#### `DELETE /v1/admin/session/{session_id}`

Delete a specific chat session.

#### `POST /v1/admin/cleanup_sessions`

Clean up sessions older than specified days.

**Request Body:**

```json
{
  "days": 30
}
```

#### `POST /v1/admin/process_directories`

Process all documents in configured directories.

### **Health & Status**


Check ChromaDB connection status.

## 📋 Detailed Phase Documentation

### **Phase 1: Foundation & Configuration Management**

**Objectives:**

- Establish clean architecture with separation of concerns
- Implement centralized configuration management
- Set up dependency injection for testability and maintainability

**Key Changes:**

1. **Centralized Configuration (`src/app/core/config.py`)**

   ```python
   class Settings:
       def __init__(self):
           self.PROJECT_NAME = "VINO API"
           self.GOOGLE_API_KEY = SecretStr(os.getenv("GOOGLE_API_KEY"))
           self.SUPABASE_URL = os.getenv("SUPABASE_URL", "")
           # ... all configuration centralized
   ```

2. **Dependency Injection (`src/app/dependencies.py`)**

   ```python
   def get_chat_service() -> ChatService:
       return ChatService(
           vector_db_service=get_vector_db_service(),
           session_storage_service=get_session_storage_service()
       )
   ```

3. **Service Refactoring**
   - All services now accept configuration via dependency injection
   - Removed global state and hardcoded configuration
   - Clean interfaces between services

**Benefits:**

-  Testable services with dependency injection
-  Single source of truth for configuration
-  Easy environment-specific configuration
-  Improved error handling and validation

### **Phase 2: Service Purification & Ingestion Pipeline**

**Objectives:**

- Create pure, single-responsibility services
- Implement document ingestion pipeline
- Separate file operations from business logic

**Key Changes:**

1. **Service Purification**

   - `VectorDBService`: Only handles vector database operations
   - `SupabaseService`: Pure client for Supabase operations
   - `FileSystemService`: Handles all file operations and storage

2. **Ingestion Pipeline (`src/app/services/ingestion_service.py`)**
   ```python
   class IngestionService:
       def process_documents(self, directory: str, collection: str):
           # Orchestrates: file discovery → processing → chunking → storage
           files = self.file_system_service.discover_files(directory)
           for file in files:
               doc = self.document_service.load_document(file)
               chunks = self.chunking_service.chunk_document(doc)
               self.vector_db_service.store_chunks(chunks, collection)
   ```

3. **Error Handling & Validation**
   - Comprehensive error handling at service boundaries
   - Input validation with Pydantic models
   - Graceful degradation for external service failures

**Benefits:**

- Clear separation of concerns
-  Reusable, composable services
-  Robust error handling (WIP)
-  Easier testing and maintenance (WIP)

### **Phase 3: Document Context in Chat**

**Objectives:**

- Enable file-specific conversations
- Implement context-aware prompt engineering
- Organize endpoints with FastAPI routers

**Key Changes:**

1. **Context-Aware Chat (`src/app/services/chat_service.py`)**

   ```python
   def chat(self, message: str, session_id: str, uploaded_file_context_name: str = None):
       if uploaded_file_context_name:
           # Query vector DB with file filter
           file_context = self.vector_db_service.query_collection(
               query=message,
               where={"source": uploaded_file_context_name}
           )
           # Inject context into prompt
           enhanced_prompt = self._build_context_prompt(message, file_context)
   ```

2. **Advanced Prompt Engineering (`src/app/prompt_engineering/builder.py`)**
   - Context injection based on file selection
   - Universal matrix prompt system
   - Dynamic prompt building based on conversation state

3. **Router Organization (`src/app/endpoints/chat.py`)**

   ```python
   @router.post("/v1/chat", response_model=ChatResponse)
   async def chat_endpoint(
       request: ChatRequest,
       chat_service: ChatService = Depends(get_chat_service)
   ):
       return chat_service.chat(
           message=request.message,
           session_id=request.session_id,
           uploaded_file_context_name=request.uploaded_file_context_name
       )
   ```

**Benefits:**

- File-specific conversations with document context
- Intelligent prompt engineering
- Clean API organization
- Enhanced user experience with contextual responses

### **Phase 4: Production Session Management**

**Objectives:**

- Move session state out of memory for scalability
- Enable horizontal scaling with stateless design
- Implement persistent session storage with Supabase

**Key Changes:**

1. **Persistent Session Storage (`src/app/services/session_storage_service.py`)**
   ```python
   class SessionStorageService:
       def get_session_data(self, session_id: str) -> Tuple[List[BaseMessage], int, str]:
           # Load from Supabase database
           result = self.supabase_service.client.table("chat_sessions")...
           
       def update_session_data(self, session_id: str, history, step, planner):
           # Persist to Supabase with fallback to memory
   ```

2. **Stateless ChatService**

   ```python
   class ChatService:
       def _get_session_data(self, session_id: str):
           if self.session_storage_service:
               return self.session_storage_service.get_session_data(session_id)
           # Fallback to memory
           
       def _update_session_data(self, session_id: str, ...):
           if self.session_storage_service:
               self.session_storage_service.update_session_data(...)
           # Fallback to memory
   ```

3. **Database Schema (Supabase)**

   ```sql
   CREATE TABLE chat_sessions (
       id SERIAL PRIMARY KEY,
       session_id VARCHAR(255) UNIQUE NOT NULL,
       conversation_history JSONB DEFAULT '[]'::jsonb,
       current_step INTEGER DEFAULT 1,
       planner_details TEXT,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
       last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );
   ```

4. **Admin Management Endpoints**
   - Session information retrieval
   - Session deletion and cleanup
   - Automatic cleanup of old sessions

**Benefits:**


- **Horizontal Scalability**: Multiple app instances share session data (WIP)
- **Persistence**: Sessions survive server restarts
- **Reliability**: Graceful fallback to memory storage (WIP)
- **Management**: Admin tools for session lifecycle
- **Performance**: Efficient JSON storage in PostgreSQL

## ⚙️ Configuration

Key configuration options in `src/app/core/config.py`:

### **Core Settings**

- `PROJECT_NAME`: Application name (default: "VINO API")
- `VERSION`: API version (default: "1.3.0")
- `GOOGLE_API_KEY`: Required Google Generative AI API key
- `SUPABASE_URL`: Supabase project URL for session storage
- `SUPABASE_ANON_KEY`: Supabase anonymous key

### **File Processing**

- `CHUNK_SIZE`: Document chunk size (configurable)
- `CHUNK_OVERLAP`: Overlap between chunks (configurable)
- `DOCUMENTS_DIR`: Framework documentation directory
- `USER_UPLOADS_DIR`: User upload directory
- `CHUNKING_DEBUG`: Enable debug mode for chunking

### **Vector Database**

- `FRAMEWORKS_COLLECTION_NAME`: Collection for framework docs
- `USER_DOCUMENTS_COLLECTION_NAME`: Collection for user docs
- `USE_CHROMA_SERVER`: Use ChromaDB server vs local storage
- `CHROMA_SERVER_HOST` / `CHROMA_SERVER_PORT`: Server configuration

### **AI Model Settings**

- `LLM_MODEL_NAME`: Google AI model (default: "gemini-1.5-pro")
- `LLM_TEMPERATURE`: Model temperature (default: 0)
- `LLM_MAX_RETRIES`: Maximum retry attempts (default: 2)

## 💡 Usage Examples

### **File-Specific Chat Conversation**

```bash
# Upload a document
curl -X POST "http://localhost:8000/v1/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@research_paper.pdf"

# Start a file-specific conversation
curl -X POST "http://localhost:8000/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the main findings in this research?",
    "uploaded_file_context_name": "research_paper.pdf",
    "mode": "chat"
  }'
```

### **General Semantic Search**

```bash
curl -X POST "http://localhost:8000/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning best practices",
    "collection": "user_documents",
    "max_results": 5
  }'
```

### **Session Management**

```bash
# Get session information
curl -X GET "http://localhost:8000/v1/admin/session/my-session-id"

# Clean up old sessions (admin)
curl -X POST "http://localhost:8000/v1/admin/cleanup_sessions" \
  -H "Content-Type: application/json" \
  -d '{"days": 30}'
```

### **Multi-turn Conversation with Context**

```bash
# First message in session
curl -X POST "http://localhost:8000/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Summarize the key concepts in this document",
    "session_id": "research-session-1",
    "uploaded_file_context_name": "research_paper.pdf"
  }'

# Follow-up question in same session
curl -X POST "http://localhost:8000/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the limitations mentioned?",
    "session_id": "research-session-1",
    "uploaded_file_context_name": "research_paper.pdf"
  }'
```

## Deployment

### **Production Considerations**

1. **Environment Variables**
   - Use secure secret management for API keys
   - Configure proper CORS origins for your frontend
   - Set up proper logging levels and monitoring

2. **Database Setup**
   - Redis is required for session storage and caching
   - Optionally use managed Supabase instance for persistent session storage
   - Set up proper database indexing for performance (if using Supabase)
   - Configure backup and recovery procedures

3. **Scaling Considerations**
   - The application is stateless and supports horizontal scaling
   - Session state is cached in Redis and optionally persisted in Supabase
   - Consider using a load balancer for multiple instances

4. **Security**
   - Implement rate limiting and authentication as needed
   - Use HTTPS in production
   - Validate and sanitize all user inputs

### **Docker Deployment**

```bash
# Full stack with Docker Compose (all services)
docker-compose --profile all up -d

# Or run services separately
docker-compose up -d redis        # Session storage
docker-compose up -d fastapi      # Backend API with embedded ChromaDB
docker-compose up -d frontend     # Reflex UI frontend
```

### **Production Docker Build**

The project uses multi-stage Docker builds with dependency separation:

```dockerfile
# FastAPI Backend (Dockerfile.fastapi)
FROM python:3.11-slim

WORKDIR /app

# Install uv for faster dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install FastAPI dependencies only
RUN uv sync --frozen --no-dev --group fastapi

# Copy application code
COPY src/ src/
COPY .env .

EXPOSE 8000

CMD ["uv", "run", "--group", "fastapi", "uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🐳 Docker Deployment

This project uses Docker Compose for easy deployment with separate services:


- **FastAPI Backend**: API server with embedded ChromaDB for vector storage
- **Reflex Frontend**: Interactive chat UI
- **Redis**: Session storage and caching

### Quick Start with Docker

```bash
# Build and start all services
docker-compose --profile all up -d --build

# View running services
docker-compose ps

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Development Profile

```bash
# Start only development services (FastAPI + ChromaDB + Redis)
docker-compose --profile dev up -d

# Start with automatic rebuilding
docker-compose --profile dev up -d --build
```

### Production Profile

```bash
# Start production services with optimizations
docker-compose --profile prod up -d

# Production with specific resource limits
docker-compose --profile prod up -d --build
```

### Individual Services

```bash
# Start only Redis (for session storage)
docker-compose up -d redis

# Start backend with embedded ChromaDB
docker-compose up -d fastapi

# Start only frontend
docker-compose up -d frontend
```

### Access Points

Once running, access the application at:

- **Reflex UI Frontend**: <http://localhost:3000>
- **FastAPI Backend**: <http://localhost:8000>
- **API Documentation**: <http://localhost:8000/docs>
- **Redis**: localhost:6379

*Note: ChromaDB is embedded within the FastAPI service and not directly accessible*

## 🧪 Testing

### **Running Tests**

```bash
# Run all tests
python -m pytest tests/

# Run specific phase tests
python -m pytest tests/test_phase1.py -v
python -m pytest tests/test_phase2.py -v
python -m pytest tests/test_phase3.py -v
python -m pytest tests/test_phase4.py -v

# Run integration tests
python -m pytest tests/test_phase3_integration.py -v

# Run with coverage
python -m pytest --cov=src tests/
```

### **Test Coverage WIP**

The test suite covers:

- ✅ Configuration management and dependency injection
- ✅ Service interactions and error handling
- ✅ Document processing and vector storage
- ✅ Context-aware chat functionality
- ✅ Session storage and persistence
- ✅ Integration scenarios and edge cases

## Troubleshooting

### **Common Issues**

1. **Session Storage Connection**

   ```bash
   Error: Cannot connect to Supabase
   Solution: Check SUPABASE_URL and SUPABASE_ANON_KEY in .env
   Fallback: Application will use Redis and memory storage automatically
   ```

2. **ChromaDB Issues**

   ```txt
   Error: ChromaDB connection failed
   Solution: Check Docker logs for FastAPI service (ChromaDB is embedded)
   Commands: docker-compose logs fastapi
   ```

3. **Google AI API Issues**

   ```txt
   Error: Invalid API key or quota exceeded
   Solution: Verify GOOGLE_API_KEY and check quota limits
   ```

4. **File Upload Problems**

   ```txt
   Error: File processing failed
   Solution: Check file permissions and supported formats
   Supported: PDF, TXT, DOCX
   ```

### **Debug Mode (WIP)**

Enable detailed logging:

```bash
# Set environment variable
export CHUNKING_DEBUG=true

# Or in .env file
CHUNKING_DEBUG=true
```

### **Health Checks**

Monitor system status:

```bash
# Check ChromaDB
curl http://localhost:8000/health/chromadb

# Check API status
curl http://localhost:8000/docs
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`python -m pytest tests/`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request


## Performance Considerations

### **Scaling Strategies**

1. **Horizontal Scaling**: Multiple FastAPI instances with shared Supabase sessions
2. **Caching**: Consider Redis for frequently accessed data
3. **Database Optimization**: Index optimization for session queries
4. **Vector Search**: ChromaDB performance tuning for large collections

### **Monitoring Recommendations**

- Session storage performance and connection pooling
- Vector database query performance
- API response times and error rates
- Memory usage and garbage collection

## License

[Add your license information here]

## Support

For questions, issues, or contributions:

- Create an issue in the GitHub repository
- Check the documentation in the `docs/` directory
- Review the test files for usage examples

---

# Uploading Documents for Context

For Supabase table and storage setup instructions, see [Supabase Setup Guide](file_upload/supabase-setup.md). Supabase is used for persistent session storage and document metadata management and must be configured before uploading documents.

To add new documents to the Knowledge Bank:

1. Place your `.md`, `.txt`, `.pdf`, or `.docx` file in the `data/kb_new/` directory.
2. Run the following command from the project root:

   ```bash
   uv run python -m file_upload.file_processor --default
   ```
3. The script will process and upload documents to both ChromaDB and Supabase, then move processed files to `data/kb/`.
4. Check the terminal output for upload status and errors.

For detailed requirements, document structure, and troubleshooting, see [Document Upload Guide](docs/upload-docs.md).



**Built with passion using FastAPI, ChromaDB, Google Generative AI, and Supabase**
