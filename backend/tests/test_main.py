"""
Test the main application setup.
"""
import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """Create a test client for the app."""
    with TestClient(app) as c:
        yield c


def test_health_check(client):
    """Test that the health check endpoint works."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "otakuhub-backend"}


def test_status_check(client):
    """Test that the status check endpoint works."""
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    assert response.json() == {"status": "operational", "service": "otakuhub-backend"}


def test_root endpoints(client):
    """Test that the app starts correctly."""
    response = client.get("/")
    assert response.status_code == 404  # FastAPI returns 404 for root path