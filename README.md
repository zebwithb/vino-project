# Vino Project

A FastAPI-based document processing and semantic search application that combines ChromaDB vector database with Google's Generative AI for intelligent document retrieval and question answering.

## Features

- **Document Processing**: Support for PDF and text file processing with intelligent chunking
- **Semantic Search**: Vector-based similarity search using Google Generative AI embeddings
- **Dual Storage**: Framework documentation and user-uploaded document collections
- **Flexible Deployment**: Local ChromaDB or Docker container support
- **RESTful API**: FastAPI-based endpoints for document management and search
- **Auto-Loading**: Automatic framework documentation loading on startup

## Architecture

- **FastAPI**: Modern web framework for building APIs
- **ChromaDB**: Vector database for document embeddings and similarity search
- **Google Generative AI**: Embedding function for semantic understanding
- **Pydantic**: Data validation and serialization
- **PyPDF2**: PDF text extraction

## Project Structure

```plaintext
vino-project/
├── src/app/
│   ├── config.py              # Configuration management
│   ├── main.py                # FastAPI application entry point
│   ├── models.py              # Pydantic data models
│   └── services/
│       ├── document_service.py    # Document processing utilities
│       └── vector_db_service.py   # ChromaDB management
├── data/
│   ├── framework_docs/        # Pre-loaded documentation
│   └── user_uploads/          # User-uploaded files
├── chromadb/                  # Local ChromaDB storage
├── docker-compose.yml         # Docker services configuration
└── requirements.txt           # Python dependencies
```

## Quick Start

### Prerequisites

- Python 3.8+
- Google Generative AI API key
- Docker (optional, for ChromaDB server mode)

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd vino-project
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:

   ```env
   GEMINI_KEY_API=your_google_api_key_here
   
   # ChromaDB Configuration (optional)
   USE_CHROMA_SERVER=false
   CHROMA_SERVER_HOST=localhost
   CHROMA_SERVER_PORT=8001
   ```

### Running the Application

#### Local Mode (Default)

```bash
# Start the FastAPI application
python -m uvicorn src.app.main:app --reload

# Access the API at http://localhost:8000
# View API docs at http://localhost:8000/docs
```

#### Docker Mode (ChromaDB Server)

```bash
# Start ChromaDB container
docker-compose up -d chromadb

# Update .env: USE_CHROMA_SERVER=true
# Then start the FastAPI application
python -m uvicorn src.app.main:app --reload
```

## API Endpoints

### Document Management

TO DO

### Search & Query

- `POST /query` - Semantic search across documents
- `POST /chat` - Interactive Q&A with document context

### Health & Status

- `GET /health/chromadb` - Check ChromaDB connection status

## Configuration

Key configuration options in `src/app/config.py`:

- `CHUNK_SIZE`: Document chunk size (default: 1000 characters)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200 characters)
- `FRAMEWORKS_COLLECTION_NAME`: Name for framework docs collection
- `USER_DOCUMENTS_COLLECTION_NAME`: Name for user docs collection
- `DOCUMENTS_DIR`: Directory for framework documentation
- `USER_UPLOADS_DIR`: Directory for user uploads

## Usage Examples

### Upload a Document

```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

### Search Documents

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "collection": "user_documents",
    "max_results": 5
  }'
```

### Interactive Chat

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain the main concepts from the uploaded documents"
  }'
```

## Development

### Adding Framework Documentation

Place PDF or text files in the `data/framework_docs/` directory. They will be automatically loaded when the application starts.

### Extending File Support

Add new file type handlers in `src/app/services/document_service.py` in the `load_single_document()` function.

### Custom Embeddings

Replace the Google Generative AI embedding function in `src/app/services/vector_db_service.py` with your preferred embedding model.

## Deployment

### Production Considerations

- Use environment variables for all sensitive configuration
- Configure proper CORS origins for your frontend
- Set up proper logging and monitoring
- Consider using a managed ChromaDB instance for production
- Implement rate limiting and authentication as needed

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or run ChromaDB separately
docker-compose up -d chromadb
```

## Troubleshooting

### Common Issues

- **ChromaDB Connection**: Check that the ChromaDB server is running if using server mode
- **API Key**: Ensure your Google Generative AI API key is properly set
- **File Uploads**: Verify the upload directory exists and has write permissions
- **PDF Processing**: Some PDFs may not extract text properly; consider OCR solutions for scanned documents

### Debugging

Enable debug logging by setting the log level in your environment or configuration.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

[Add your license information here]

## Support

[Add support/contact information here]
