"""
Authentication Tests
Tests for user registration, login, and authentication flows
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.security import verify_password


@pytest.mark.auth
@pytest.mark.asyncio
class TestUserRegistration:
    """Test user registration endpoint"""
    
    async def test_register_new_user(self, client: AsyncClient, sample_user_data: dict):
        """Test successful user registration"""
        response = await client.post("/api/v1/auth/register", json=sample_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == sample_user_data["email"]
        assert data["full_name"] == sample_user_data["full_name"]
        assert "id" in data
        assert "hashed_password" not in data
    
    async def test_register_duplicate_email(
        self,
        client: AsyncClient,
        test_user: User,
        sample_user_data: dict
    ):
        """Test registration with existing email fails"""
        sample_user_data["email"] = test_user.email
        response = await client.post("/api/v1/auth/register", json=sample_user_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email format"""
        data = {
            "email": "invalid-email",
            "password": "SecurePassword123!",
            "full_name": "Test User"
        }
        response = await client.post("/api/v1/auth/register", json=data)
        
        assert response.status_code == 422  # Validation error
    
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password"""
        data = {
            "email": "test@example.com",
            "password": "123",  # Too short
            "full_name": "Test User"
        }
        response = await client.post("/api/v1/auth/register", json=data)
        
        assert response.status_code == 422


@pytest.mark.auth
@pytest.mark.asyncio
class TestUserLogin:
    """Test user login endpoint"""
    
    async def test_login_success(self, client: AsyncClient, test_user: User):
        """Test successful login"""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_login_wrong_password(self, client: AsyncClient, test_user: User):
        """Test login with incorrect password"""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent email"""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "somepassword"
            }
        )
        
        assert response.status_code == 401
    
    async def test_login_inactive_user(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test login with inactive user account"""
        test_user.is_active = False
        await db_session.commit()
        
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == 401
        assert "inactive" in response.json()["detail"].lower()


@pytest.mark.auth
@pytest.mark.asyncio
class TestTokenRefresh:
    """Test token refresh endpoint"""
    
    async def test_refresh_token_success(
        self,
        client: AsyncClient,
        test_user: User
    ):
        """Test successful token refresh"""
        # First login to get refresh token
        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "testpassword123"
            }
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Use refresh token to get new access token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Test refresh with invalid token"""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        
        assert response.status_code == 401


@pytest.mark.auth
@pytest.mark.asyncio
class TestPasswordReset:
    """Test password reset flow"""
    
    async def test_password_reset_request(
        self,
        client: AsyncClient,
        test_user: User
    ):
        """Test password reset request"""
        response = await client.post(
            "/api/v1/auth/password-reset-request",
            json={"email": test_user.email}
        )
        
        assert response.status_code == 200
        assert "email sent" in response.json()["message"].lower()
    
    async def test_password_reset_nonexistent_email(self, client: AsyncClient):
        """Test password reset for non-existent email"""
        response = await client.post(
            "/api/v1/auth/password-reset-request",
            json={"email": "nonexistent@example.com"}
        )
        
        # Should return 200 to prevent email enumeration
        assert response.status_code == 200


@pytest.mark.auth
@pytest.mark.asyncio
class TestEmailVerification:
    """Test email verification flow"""
    
    async def test_verify_email_success(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test successful email verification"""
        # Set user as unverified
        test_user.is_verified = False
        await db_session.commit()
        
        # Create verification token
        from app.core.security import create_email_verification_token
        token = create_email_verification_token(test_user.email)
        
        response = await client.post(
            "/api/v1/auth/verify-email",
            json={"token": token}
        )
        
        assert response.status_code == 200
        assert "verified" in response.json()["message"].lower()
    
    async def test_verify_email_invalid_token(self, client: AsyncClient):
        """Test email verification with invalid token"""
        response = await client.post(
            "/api/v1/auth/verify-email",
            json={"token": "invalid_token"}
        )
        
        assert response.status_code == 400


@pytest.mark.auth
@pytest.mark.asyncio
class TestProtectedEndpoints:
    """Test authentication required for protected endpoints"""
    
    async def test_access_protected_without_token(self, client: AsyncClient):
        """Test accessing protected endpoint without token"""
        response = await client.get("/api/v1/users/me")
        
        assert response.status_code == 401
    
    async def test_access_protected_with_invalid_token(self, client: AsyncClient):
        """Test accessing protected endpoint with invalid token"""
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    async def test_access_protected_with_valid_token(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test accessing protected endpoint with valid token"""
        response = await client.get("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "id" in data


# Made with Bob