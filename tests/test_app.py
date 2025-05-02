import pytest
from fastapi.testclient import TestClient
from src.app import app
import time

client = TestClient(app)

def test_summarize_endpoint():
    response = client.post(
        "/v1/summarize",
        json={"text": "This is a long text that needs to be summarized. It contains multiple sentences and should be reduced to about thirty words while maintaining the key points and meaning of the original text."}
    )
    assert response.status_code == 200
    assert "summary" in response.json()
    assert isinstance(response.json()["summary"], str)

def test_similarity_endpoint():
    response = client.post(
        "/v1/similarity",
        json={
            "query": "Hello world",
            "texts": ["Hello world", "Goodbye world", "Something completely different"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "closest_text" in data
    assert "score" in data
    assert isinstance(data["score"], float)
    assert 0 <= data["score"] <= 1

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert isinstance(data["uptime"], float)
    assert data["uptime"] >= 0

def test_invalid_input():
    # Test empty text for summarize
    response = client.post("/v1/summarize", json={"text": ""})
    assert response.status_code == 422

    # Test empty query for similarity
    response = client.post("/v1/similarity", json={"query": "", "texts": ["test"]})
    assert response.status_code == 422

    # Test empty texts array for similarity
    response = client.post("/v1/similarity", json={"query": "test", "texts": []})
    assert response.status_code == 422