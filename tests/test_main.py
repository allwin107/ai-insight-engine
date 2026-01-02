"""
Tests for main API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.unit
class TestMainEndpoints:
    """Test main API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "AI Data Insight Engine API"
        assert data["status"] == "running"
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_api_v1_root(self):
        """Test API v1 root"""
        response = client.get("/api/v1")
        assert response.status_code == 200
        data = response.json()
        assert "endpoints" in data
        assert "auth" in data["endpoints"]
        assert "upload" in data["endpoints"]
    
    def test_docs_available(self):
        """Test API documentation is available"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_404_endpoint(self):
        """Test non-existent endpoint returns 404"""
        response = client.get("/nonexistent")
        assert response.status_code == 404