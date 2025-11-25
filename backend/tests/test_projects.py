"""
Test Suite for Project Management
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)


@pytest.fixture
def auth_headers(valid_token: str):
    """Return authorization headers with valid token"""
    return {"Authorization": f"Bearer {valid_token}"}


class TestProjectCreation:
    """Test project creation functionality"""
    
    def test_create_project_success(self, auth_headers: dict):
        """Test successful project creation"""
        project_data = {
            "title": "Q4 Marketing Report",
            "description": "Quarterly marketing performance",
            "document_type": "document",
            "metadata": {"industry": "tech"}
        }
        response = client.post(
            "/api/projects",
            json=project_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["title"] == "Q4 Marketing Report"
    
    def test_create_project_without_auth(self):
        """Test project creation without authentication"""
        project_data = {
            "title": "Unauthorized Project",
            "document_type": "document"
        }
        response = client.post("/api/projects", json=project_data)
        
        assert response.status_code == 403
    
    def test_create_project_invalid_type(self, auth_headers: dict):
        """Test project creation with invalid document type"""
        project_data = {
            "title": "Invalid Project",
            "document_type": "invalid"  # Not 'document' or 'presentation'
        }
        response = client.post(
            "/api/projects",
            json=project_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422


class TestProjectRetrieval:
    """Test project retrieval functionality"""
    
    @pytest.fixture(autouse=True)
    def setup_project(self, auth_headers: dict):
        """Create a test project"""
        project_data = {
            "title": "Test Project",
            "document_type": "document"
        }
        response = client.post(
            "/api/projects",
            json=project_data,
            headers=auth_headers
        )
        self.project_id = response.json()["data"]["project_id"]
    
    def test_list_projects(self, auth_headers: dict):
        """Test listing projects"""
        response = client.get(
            "/api/projects",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "projects" in data["data"]
        assert data["data"]["total"] >= 0
    
    def test_get_project_by_id(self, auth_headers: dict):
        """Test getting specific project"""
        response = client.get(
            f"/api/projects/{self.project_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["project_id"] == self.project_id
    
    def test_get_nonexistent_project(self, auth_headers: dict):
        """Test getting non-existent project"""
        response = client.get(
            "/api/projects/00000000-0000-0000-0000-000000000000",
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestProjectUpdate:
    """Test project update functionality"""
    
    @pytest.fixture(autouse=True)
    def setup_project(self, auth_headers: dict):
        """Create a test project"""
        project_data = {
            "title": "Original Title",
            "document_type": "document"
        }
        response = client.post(
            "/api/projects",
            json=project_data,
            headers=auth_headers
        )
        self.project_id = response.json()["data"]["project_id"]
    
    def test_update_project_title(self, auth_headers: dict):
        """Test updating project title"""
        update_data = {
            "title": "Updated Title",
            "status": "in_progress"
        }
        response = client.put(
            f"/api/projects/{self.project_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["title"] == "Updated Title"
        assert data["data"]["status"] == "in_progress"


class TestProjectDeletion:
    """Test project deletion functionality"""
    
    @pytest.fixture(autouse=True)
    def setup_project(self, auth_headers: dict):
        """Create a test project"""
        project_data = {
            "title": "Project to Delete",
            "document_type": "document"
        }
        response = client.post(
            "/api/projects",
            json=project_data,
            headers=auth_headers
        )
        self.project_id = response.json()["data"]["project_id"]
    
    def test_delete_project(self, auth_headers: dict):
        """Test project deletion"""
        response = client.delete(
            f"/api/projects/{self.project_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify project is deleted
        get_response = client.get(
            f"/api/projects/{self.project_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404


# Integration test
class TestProjectWorkflow:
    """End-to-end project workflow"""
    
    def test_complete_project_workflow(self, auth_headers: dict):
        """Test: create → retrieve → update → delete project"""
        # 1. Create
        project_data = {
            "title": "Workflow Test Project",
            "description": "Testing complete workflow",
            "document_type": "presentation"
        }
        create_response = client.post(
            "/api/projects",
            json=project_data,
            headers=auth_headers
        )
        assert create_response.status_code == 201
        project_id = create_response.json()["data"]["project_id"]
        
        # 2. Retrieve
        get_response = client.get(
            f"/api/projects/{project_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 200
        
        # 3. Update
        update_response = client.put(
            f"/api/projects/{project_id}",
            json={"status": "completed"},
            headers=auth_headers
        )
        assert update_response.status_code == 200
        
        # 4. Delete
        delete_response = client.delete(
            f"/api/projects/{project_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 204


@pytest.fixture
def valid_token():
    """Generate a valid auth token for testing"""
    from app.core.security import SecurityUtils
    return SecurityUtils.create_access_token({"sub": "test-user-id"})
