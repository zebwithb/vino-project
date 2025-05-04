# AI Text Utility API

A FastAPI-based REST API that provides text summarization and semantic similarity features using OpenAI's API.

## Features

- Text summarization endpoint (`/v1/summarize`)
- Semantic similarity comparison (`/v1/similarity`)
- Health check endpoint (`/health`)

## Prerequisites

- Docker and Docker Compose
- OpenAI API key

## Quick Start

1. Clone the repository
2. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
3. Start the service:
   ```bash
   docker-compose up --build
   ```
4. The API will be available at `http://localhost:8000`

## API Endpoints

### 1. Summarize Text
```
POST /v1/summarize
```
Request body:
```json
{
    "text": "Your long text here"
}
```
Response:
```json
{
    "summary": "Concise summary of the text"
}
```

### 2. Find Similar Text
```
POST /v1/similarity
```
Request body:
```json
{
    "query": "Your query text",
    "texts": ["Text A", "Text B", "Text C"]
}
```
Response:
```json
{
    "closest_text": "Most similar text",
    "score": 0.95
}
```

### 3. Health Check
```
GET /health
```
Response:
```json
{
    "status": "ok",
    "uptime": 123.45
}
```

## How to Build, Run, and Test

### Prerequisites

- Docker and Docker Compose
- OpenAI API key

### Build & Run

1. Clone the repository.
2. Create a `.env` file in the root directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
3. Build and start the service:
   ```
   docker-compose up --build
   ```
   The API will be available at [http://localhost:8000](http://localhost:8000).

### Testing

To run tests:
```
docker-compose run api pytest tests/
```

### API Documentation

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Architectural Decisions

- **FastAPI** was chosen for its speed, async support, and automatic OpenAPI documentation.
- **Docker** ensures consistent deployment and easy local development.
- **OpenAI API** is used for summarization and semantic similarity due to its state-of-the-art language models.
- **Chunking Strategy:** Recursive character splitting (see `docs/process.md`) is used for text chunking, balancing simplicity and generality.
- **Prompting Strategy:** Tiered-based prompting is implemented for adaptability and future extensibility (see `docs/process.md` for alternatives considered).
- **Input validation** is handled with Pydantic models for security and reliability.
- **Testing** is done with Pytest for simplicity and integration with Docker.

For detailed rationale and diagrams, see [docs/process.md](docs/process.md).

## Error Handling

- 400-level errors for invalid input
- 500-level errors for internal server errors
- Detailed error messages in the response body

## Security

- API key is handled via environment variables
- Input validation using Pydantic models
- No sensitive data in logs or error messages
