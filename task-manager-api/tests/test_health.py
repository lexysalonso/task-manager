"""Health endpoint tests."""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_response_time() -> None:
    """Health check should respond in under 100ms."""
    response = client.get("/api/v1/health")
    assert response.elapsed.total_seconds() < 0.1
