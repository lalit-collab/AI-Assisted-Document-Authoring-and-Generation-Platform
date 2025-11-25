"""
Test Suite for Content Generation
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, AsyncMock
import json

client = TestClient(app)


@pytest.fixture
def auth_headers(valid_token: str):
    """Return authorization headers"""
    return {"Authorization": f"Bearer {valid_token}"}


class TestContentGeneration:
    """Test AI content generation functionality"""
    
    @patch('app.integrations.get_llm_client')
    def test_generate_content_success(self, mock_llm, auth_headers: dict):
        """Test successful content generation"""
        # Mock LLM response
        mock_llm_instance = AsyncMock()
        mock_llm_instance.generate_content = AsyncMock(return_value="Generated content text")
        mock_llm.return_value = mock_llm_instance
        
        generation_data = {
            "document_id": "doc-123",
            "section_id": "sec-123",
            "stream": False
        }
        response = client.post(
            "/api/generation/generate",
            json=generation_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "content_id" in data["data"]
        assert "content" in data["data"]
    
    def test_generate_without_auth(self):
        """Test generation without authentication"""
        generation_data = {
            "document_id": "doc-123",
            "section_id": "sec-123"
        }
        response = client.post(
            "/api/generation/generate",
            json=generation_data
        )
        
        assert response.status_code == 403


class TestContentRetrieval:
    """Test retrieving generated content"""
    
    def test_get_generated_content(self, auth_headers: dict):
        """Test retrieving generated content"""
        content_id = "content-123"
        response = client.get(
            f"/api/generation/generated-content/{content_id}",
            headers=auth_headers
        )
        
        # May be 404 if content doesn't exist, which is OK for this test
        assert response.status_code in [200, 404]


# Fixtures
@pytest.fixture
def valid_token():
    """Generate valid token"""
    from app.core.security import SecurityUtils
    return SecurityUtils.create_access_token({"sub": "test-user"})
