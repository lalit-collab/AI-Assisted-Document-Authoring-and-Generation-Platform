"""
Test Suite for Authentication
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import SecurityUtils
from app.models import User
from sqlalchemy.orm import Session

client = TestClient(app)


class TestUserRegistration:
    """Test user registration functionality"""
    
    def test_register_user_success(self, db_session: Session):
        """Test successful user registration"""
        user_data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "first_name": "John",
            "last_name": "Doe"
        }
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["email"] == "newuser@example.com"
    
    def test_register_duplicate_email(self, db_session: Session):
        """Test registration with existing email fails"""
        # First registration
        user_data = {
            "email": "existing@example.com",
            "password": "SecurePass123!",
            "first_name": "John"
        }
        client.post("/api/auth/register", json=user_data)
        
        # Second registration with same email
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 409
    
    def test_register_weak_password(self):
        """Test registration with weak password fails"""
        user_data = {
            "email": "test@example.com",
            "password": "weak",  # Too short
            "first_name": "John"
        }
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 422  # Validation error
    
    def test_register_invalid_email(self):
        """Test registration with invalid email fails"""
        user_data = {
            "email": "invalid-email",
            "password": "SecurePass123!",
            "first_name": "John"
        }
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 422


class TestUserLogin:
    """Test user login functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self, db_session: Session):
        """Setup test user"""
        user_data = {
            "email": "testuser@example.com",
            "password": "TestPass123!",
            "first_name": "Test"
        }
        client.post("/api/auth/register", json=user_data)
    
    def test_login_success(self):
        """Test successful login"""
        credentials = {
            "email": "testuser@example.com",
            "password": "TestPass123!"
        }
        response = client.post("/api/auth/login", json=credentials)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["token_type"] == "Bearer"
    
    def test_login_invalid_password(self):
        """Test login with invalid password"""
        credentials = {
            "email": "testuser@example.com",
            "password": "WrongPassword!"
        }
        response = client.post("/api/auth/login", json=credentials)
        
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self):
        """Test login with non-existent user"""
        credentials = {
            "email": "nonexistent@example.com",
            "password": "TestPass123!"
        }
        response = client.post("/api/auth/login", json=credentials)
        
        assert response.status_code == 401


class TestTokenRefresh:
    """Test token refresh functionality"""
    
    def test_refresh_token_success(self, valid_refresh_token: str):
        """Test successful token refresh"""
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": valid_refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data["data"]
    
    def test_refresh_invalid_token(self):
        """Test refresh with invalid token"""
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        
        assert response.status_code == 401


class TestPasswordHashing:
    """Test password security"""
    
    def test_password_hashing(self):
        """Test password is properly hashed"""
        password = "MySecurePassword123!"
        hashed = SecurityUtils.hash_password(password)
        
        # Password should be different from hash
        assert hashed != password
        # Hash should be longer
        assert len(hashed) > len(password)
    
    def test_password_verification(self):
        """Test password verification"""
        password = "MySecurePassword123!"
        hashed = SecurityUtils.hash_password(password)
        
        # Correct password should verify
        assert SecurityUtils.verify_password(password, hashed) is True
        
        # Wrong password should not verify
        assert SecurityUtils.verify_password("WrongPassword", hashed) is False


# Integration tests
class TestAuthenticationFlow:
    """End-to-end authentication flow tests"""
    
    def test_full_auth_flow(self):
        """Test complete auth flow: register → login → access protected resource"""
        # 1. Register
        user_data = {
            "email": "flowtest@example.com",
            "password": "FlowTest123!",
            "first_name": "Flow"
        }
        register_response = client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == 201
        
        # 2. Login
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": "flowtest@example.com",
                "password": "FlowTest123!"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["data"]["access_token"]
        
        # 3. Access protected resource
        headers = {"Authorization": f"Bearer {token}"}
        me_response = client.get("/api/auth/me", headers=headers)
        assert me_response.status_code == 200
        assert me_response.json()["data"]["email"] == "flowtest@example.com"


# Fixtures
@pytest.fixture
def valid_refresh_token():
    """Generate a valid refresh token for testing"""
    return SecurityUtils.create_refresh_token({"sub": "test-user-id"})
