import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from src.main import app, start_time
from src.app.services.text_analysis import split_text_recursively
import time
import openai

@pytest.fixture(autouse=True)
def mock_openai(mocker):
    mock_chat_response = MagicMock()
    mock_chat_response.choices = [MagicMock(message=MagicMock(content="Mocked summary."))]
    mock_chat_create = AsyncMock(return_value=mock_chat_response)
    mocker.patch('src.app.services.text_analysis.client.chat.completions.create', new=mock_chat_create)

    mock_embedding_data_single = MagicMock(embedding=[0.1, 0.2, 0.3])
    mock_embedding_data_list = [
        MagicMock(embedding=[0.1, 0.2, 0.3]),
        MagicMock(embedding=[0.4, 0.5, 0.6]),
        MagicMock(embedding=[0.7, 0.8, 0.9])
    ]

    async def embedding_side_effect(*args, **kwargs):
        input_data = kwargs.get('input', [])
        if isinstance(input_data, str) or len(input_data) == 1:
            return MagicMock(data=[mock_embedding_data_single])
        else:
            return MagicMock(data=mock_embedding_data_list)

    mock_embedding_create = AsyncMock(side_effect=embedding_side_effect)
    mocker.patch('src.app.services.text_analysis.client.embeddings.create', new=mock_embedding_create)

    return mock_chat_create, mock_embedding_create

client = TestClient(app)

# --- Test Text Chunking ---

def test_split_text_recursively_happy_path():
    """Tests basic recursive splitting happy path."""
    text = "This is the first sentence. This is the second sentence. This is the third sentence, which is significantly longer to ensure it gets split based on size if necessary."
    chunk_size = 50
    chunks = split_text_recursively(text, chunk_size=chunk_size, chunk_overlap=10)

    assert isinstance(chunks, list)
    assert len(chunks) > 1 # Check that splitting occurred
    assert all(isinstance(chunk, str) for chunk in chunks)
    assert chunks[0].startswith("This is the first sentence.")
    # Basic check that chunks are roughly within the size limit (allowing for overlap and separator respect)
    assert all(len(chunk) <= chunk_size + 20 for chunk in chunks) # Allow some leeway

# --- Existing API Tests ---

def test_summarize_endpoint_with_mock(mock_openai):
    mock_chat_create, _ = mock_openai
    response = client.post(
        "/v1/summarize",
        json={"text": "This is a long text that needs to be summarized."}
    )
    assert response.status_code == 200
    assert response.json() == {"summary": "Mocked summary."}
    mock_chat_create.assert_awaited_once()
    call_args = mock_chat_create.await_args.kwargs
    assert call_args['model'] == "gpt-4.1"
    assert call_args['messages'][-1]['content'] == "This is a long text that needs to be summarized."

def test_similarity_endpoint_with_mock(mock_openai):
    _, mock_embedding_create = mock_openai
    texts_input = ["Hello world", "Goodbye world", "Something else"]
    response = client.post(
        "/v1/similarity",
        json={
            "query": "Hello world query",
            "texts": texts_input
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["closest_text"] == "Hello world"
    assert isinstance(data["score"], float)
    assert 0 <= data["score"] <= 1
    assert data["score"] == pytest.approx(1.0)
    assert mock_embedding_create.await_count == 2

    query_call_found = False
    texts_call_found = False
    for call in mock_embedding_create.await_args_list:
        kwargs = call.kwargs
        # Check if the input is a list containing the query string
        if kwargs.get('input') == ["Hello world query"]:
            assert kwargs.get('model') == "text-embedding-3-small"
            query_call_found = True
        elif kwargs.get('input') == texts_input:
            assert kwargs.get('model') == "text-embedding-3-small"
            texts_call_found = True

    assert query_call_found
    assert texts_call_found

def test_health_endpoint():
    time.sleep(0.1)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert isinstance(data["uptime"], float)
    assert data["uptime"] > 0
    assert data["uptime"] == pytest.approx(time.time() - start_time, abs=0.1)

def test_invalid_input_summarize():
    response = client.post("/v1/summarize", json={"text": ""})
    assert response.status_code == 422

    response = client.post("/v1/summarize", json={})
    assert response.status_code == 422

    response = client.post("/v1/summarize", json={"text": 123})
    assert response.status_code == 422

def test_invalid_input_similarity():
    response = client.post("/v1/similarity", json={"query": "", "texts": ["test"]})
    assert response.status_code == 422

    response = client.post("/v1/similarity", json={"query": "test", "texts": []})
    assert response.status_code == 422

    response = client.post("/v1/similarity", json={"texts": ["test"]})
    assert response.status_code == 422

    response = client.post("/v1/similarity", json={"query": "test"})
    assert response.status_code == 422

    response = client.post("/v1/similarity", json={"query": 123, "texts": ["test"]})
    assert response.status_code == 422

    response = client.post("/v1/similarity", json={"query": "test", "texts": "not a list"})
    assert response.status_code == 422

    response = client.post("/v1/similarity", json={"query": "test", "texts": ["test", 123]})
    assert response.status_code == 422

def test_summarize_api_error(mocker):
    mock_chat_create = AsyncMock(side_effect=openai.APIError("API Error", request=None, body=None))
    mocker.patch('src.app.services.text_analysis.client.chat.completions.create', new=mock_chat_create)

    response = client.post(
        "/v1/summarize",
        json={"text": "This text will cause an error."}
    )
    assert response.status_code == 500
    assert "API Error" in response.json()["detail"]
    mock_chat_create.assert_awaited_once()

def test_similarity_api_error_query(mocker):
    mock_embedding_create = AsyncMock(side_effect=openai.APIError("Embedding API Error", request=None, body=None))
    mocker.patch('src.app.services.text_analysis.client.embeddings.create', new=mock_embedding_create)

    response = client.post(
        "/v1/similarity",
        json={"query": "test query", "texts": ["text1", "text2"]}
    )
    assert response.status_code == 500
    assert "Embedding API Error" in response.json()["detail"]
    mock_embedding_create.assert_awaited_once()

def test_similarity_api_error_texts(mocker):
    mock_embedding_create = AsyncMock()
    mock_embedding_create.side_effect = [
        MagicMock(data=[MagicMock(embedding=[0.1, 0.2, 0.3])]),
        openai.APIError("Embedding API Error", request=None, body=None)
    ]
    mocker.patch('src.app.services.text_analysis.client.embeddings.create', new=mock_embedding_create)

    response = client.post(
        "/v1/similarity",
        json={"query": "test query", "texts": ["text1", "text2"]}
    )
    assert response.status_code == 500
    assert "Embedding API Error" in response.json()["detail"]
    assert mock_embedding_create.await_count == 2