"""
Financial Accounts Tests
Tests for account management endpoints
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.account import FinancialAccount


@pytest.mark.financial
@pytest.mark.asyncio
class TestAccountCreation:
    """Test account creation endpoint"""
    
    async def test_create_account_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        sample_account_data: dict
    ):
        """Test successful account creation"""
        response = await client.post(
            "/api/v1/accounts",
            json=sample_account_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["account_name"] == sample_account_data["account_name"]
        assert data["balance"] == sample_account_data["balance"]
        assert "id" in data
    
    async def test_create_account_unauthorized(
        self,
        client: AsyncClient,
        sample_account_data: dict
    ):
        """Test account creation without authentication"""
        response = await client.post("/api/v1/accounts", json=sample_account_data)
        
        assert response.status_code == 401
    
    async def test_create_account_invalid_type(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test account creation with invalid account type"""
        data = {
            "account_type": "invalid_type",
            "institution_name": "Test Bank",
            "account_name": "Test Account",
            "balance": 1000.00,
            "currency": "USD"
        }
        response = await client.post(
            "/api/v1/accounts",
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 422


@pytest.mark.financial
@pytest.mark.asyncio
class TestAccountRetrieval:
    """Test account retrieval endpoints"""
    
    async def test_get_account_by_id(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_account: FinancialAccount
    ):
        """Test getting account by ID"""
        response = await client.get(
            f"/api/v1/accounts/{test_account.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_account.id)
        assert data["account_name"] == test_account.account_name
    
    async def test_get_nonexistent_account(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting non-existent account"""
        import uuid
        fake_id = uuid.uuid4()
        response = await client.get(
            f"/api/v1/accounts/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    async def test_list_accounts(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_account: FinancialAccount
    ):
        """Test listing user accounts"""
        response = await client.get("/api/v1/accounts", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(acc["id"] == str(test_account.id) for acc in data)
    
    async def test_get_account_summary(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_account: FinancialAccount
    ):
        """Test getting financial summary"""
        response = await client.get(
            "/api/v1/accounts/summary",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_assets" in data
        assert "total_liabilities" in data
        assert "accounts_by_type" in data
        assert "net_worth" in data


@pytest.mark.financial
@pytest.mark.asyncio
class TestAccountUpdate:
    """Test account update endpoint"""
    
    async def test_update_account_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_account: FinancialAccount
    ):
        """Test successful account update"""
        update_data = {
            "account_name": "Updated Account Name",
            "balance": 2000.00
        }
        response = await client.put(
            f"/api/v1/accounts/{test_account.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["account_name"] == update_data["account_name"]
        assert data["balance"] == update_data["balance"]
    
    async def test_update_nonexistent_account(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test updating non-existent account"""
        import uuid
        fake_id = uuid.uuid4()
        response = await client.put(
            f"/api/v1/accounts/{fake_id}",
            json={"account_name": "Test"},
            headers=auth_headers
        )
        
        assert response.status_code == 404


@pytest.mark.financial
@pytest.mark.asyncio
class TestAccountDeletion:
    """Test account deletion endpoint"""
    
    async def test_delete_account_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test successful account deletion"""
        # Create a new account to delete
        from app.models.account import AccountType
        account = FinancialAccount(
            user_id=test_user.id,
            account_type=AccountType.SAVINGS,
            institution_name="Test Bank",
            account_name="To Delete",
            balance=500.00,
            currency="USD"
        )
        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)
        
        response = await client.delete(
            f"/api/v1/accounts/{account.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
    
    async def test_delete_nonexistent_account(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test deleting non-existent account"""
        import uuid
        fake_id = uuid.uuid4()
        response = await client.delete(
            f"/api/v1/accounts/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404


@pytest.mark.financial
@pytest.mark.asyncio
class TestAccountFiltering:
    """Test account filtering and pagination"""
    
    async def test_filter_by_account_type(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_account: FinancialAccount
    ):
        """Test filtering accounts by type"""
        response = await client.get(
            f"/api/v1/accounts?account_type={test_account.account_type.value}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(acc["account_type"] == test_account.account_type.value for acc in data)
    
    async def test_pagination(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test account pagination"""
        response = await client.get(
            "/api/v1/accounts?skip=0&limit=5",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5


# Made with Bob