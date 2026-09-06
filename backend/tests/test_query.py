import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add app directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    """Test GET /health returns 200 OK and expected schema."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "vector_store_status" in data
    assert "collection_count" in data
    assert "ollama_model" in data

def test_query_happy_path():
    """Test POST /query happy path with valid question input."""
    payload = {
        "question": "How do I troubleshoot Windows Laptop Slow Performance & WinDbg Memory Dump Diagnostics?",
        "top_k": 3
    }
    response = client.post("/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == payload["question"]
    assert "answer" in data
    assert len(data["answer"]) > 0
    assert "sources" in data
    assert isinstance(data["sources"], list)

def test_query_invalid_input_422():
    """Test POST /query with invalid payload (missing question or question too short) expects 422 Unprocessable Entity."""
    # Test empty question (violates min_length=2 requirement in pydantic schema)
    invalid_payload = {
        "question": "",
        "top_k": 3
    }
    response = client.post("/query", json=invalid_payload)
    assert response.status_code == 422

def test_query_invalid_types_422():
    """Test POST /query with invalid data type for top_k expects 422."""
    invalid_payload = {
        "question": "Valid technical question",
        "top_k": "invalid_string_instead_of_int"
    }
    response = client.post("/query", json=invalid_payload)
    assert response.status_code == 422
