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

## Development

### Running Tests
```bash
docker-compose run api pytest tests/
```

### API Documentation
Once the service is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Error Handling

- 400-level errors for invalid input
- 500-level errors for internal server errors
- Detailed error messages in the response body

## Security

- API key is handled via environment variables
- Input validation using Pydantic models
- No sensitive data in logs or error messages
