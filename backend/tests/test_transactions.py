"""
Transaction Tests
Tests for transaction management endpoints
"""
import pytest
from datetime import date, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.account import FinancialAccount
from app.models.transaction import Transaction, TransactionType, TransactionCategory


@pytest.mark.financial
@pytest.mark.asyncio
class TestTransactionCreation:
    """Test transaction creation endpoint"""
    
    async def test_create_transaction_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_account: FinancialAccount,
        sample_transaction_data: dict
    ):
        """Test successful transaction creation"""
        response = await client.post(
            "/api/v1/transactions",
            json=sample_transaction_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["amount"] == sample_transaction_data["amount"]
        assert data["transaction_type"] == sample_transaction_data["transaction_type"]
        assert "id" in data
    
    async def test_create_transaction_unauthorized(
        self,
        client: AsyncClient,
        sample_transaction_data: dict
    ):
        """Test transaction creation without authentication"""
        response = await client.post(
            "/api/v1/transactions",
            json=sample_transaction_data
        )
        
        assert response.status_code == 401
    
    async def test_create_transaction_invalid_account(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test transaction creation with invalid account ID"""
        import uuid
        data = {
            "account_id": str(uuid.uuid4()),
            "transaction_date": date.today().isoformat(),
            "amount": 100.00,
            "transaction_type": "debit",
            "category": "groceries"
        }
        response = await client.post(
            "/api/v1/transactions",
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.financial
@pytest.mark.asyncio
class TestTransactionRetrieval:
    """Test transaction retrieval endpoints"""
    
    async def test_get_transaction_by_id(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_transaction: Transaction
    ):
        """Test getting transaction by ID"""
        response = await client.get(
            f"/api/v1/transactions/{test_transaction.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_transaction.id)
        assert data["amount"] == float(test_transaction.amount)
    
    async def test_get_nonexistent_transaction(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting non-existent transaction"""
        import uuid
        fake_id = uuid.uuid4()
        response = await client.get(
            f"/api/v1/transactions/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    async def test_list_transactions(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_transaction: Transaction
    ):
        """Test listing user transactions"""
        response = await client.get(
            "/api/v1/transactions",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "transactions" in data
        assert "total" in data
        assert isinstance(data["transactions"], list)
        assert len(data["transactions"]) >= 1
    
    async def test_list_transactions_with_pagination(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_transaction: Transaction
    ):
        """Test transaction pagination"""
        response = await client.get(
            "/api/v1/transactions?page=1&page_size=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert len(data["transactions"]) <= 10


@pytest.mark.financial
@pytest.mark.asyncio
class TestTransactionFiltering:
    """Test transaction filtering"""
    
    async def test_filter_by_account(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_account: FinancialAccount,
        test_transaction: Transaction
    ):
        """Test filtering transactions by account"""
        response = await client.get(
            f"/api/v1/transactions?account_id={test_account.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(
            txn["account_id"] == str(test_account.id)
            for txn in data["transactions"]
        )
    
    async def test_filter_by_type(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_transaction: Transaction
    ):
        """Test filtering by transaction type"""
        response = await client.get(
            f"/api/v1/transactions?transaction_type={test_transaction.transaction_type.value}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(
            txn["transaction_type"] == test_transaction.transaction_type.value
            for txn in data["transactions"]
        )
    
    async def test_filter_by_category(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_transaction: Transaction
    ):
        """Test filtering by category"""
        if test_transaction.category:
            response = await client.get(
                f"/api/v1/transactions?category={test_transaction.category.value}",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert all(
                txn["category"] == test_transaction.category.value
                for txn in data["transactions"]
            )
    
    async def test_filter_by_date_range(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_transaction: Transaction
    ):
        """Test filtering by date range"""
        start_date = (date.today() - timedelta(days=7)).isoformat()
        end_date = date.today().isoformat()
        
        response = await client.get(
            f"/api/v1/transactions?start_date={start_date}&end_date={end_date}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["transactions"], list)
    
    async def test_filter_by_amount_range(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test filtering by amount range"""
        response = await client.get(
            "/api/v1/transactions?min_amount=10&max_amount=100",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        for txn in data["transactions"]:
            assert 10 <= txn["amount"] <= 100
    
    async def test_search_transactions(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_transaction: Transaction
    ):
        """Test searching transactions"""
        search_term = "Test"
        response = await client.get(
            f"/api/v1/transactions?search={search_term}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["transactions"], list)


@pytest.mark.financial
@pytest.mark.asyncio
class TestTransactionUpdate:
    """Test transaction update endpoint"""
    
    async def test_update_transaction_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_transaction: Transaction
    ):
        """Test successful transaction update"""
        update_data = {
            "description": "Updated description",
            "amount": 75.00,
            "category": "restaurants"
        }
        response = await client.put(
            f"/api/v1/transactions/{test_transaction.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == update_data["description"]
        assert data["amount"] == update_data["amount"]
        assert data["category"] == update_data["category"]
    
    async def test_update_nonexistent_transaction(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test updating non-existent transaction"""
        import uuid
        fake_id = uuid.uuid4()
        response = await client.put(
            f"/api/v1/transactions/{fake_id}",
            json={"description": "Test"},
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    async def test_partial_update_transaction(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_transaction: Transaction
    ):
        """Test partial transaction update"""
        original_amount = test_transaction.amount
        update_data = {"description": "Only description updated"}
        
        response = await client.put(
            f"/api/v1/transactions/{test_transaction.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == update_data["description"]
        assert data["amount"] == float(original_amount)


@pytest.mark.financial
@pytest.mark.asyncio
class TestTransactionDeletion:
    """Test transaction deletion endpoint"""
    
    async def test_delete_transaction_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User,
        test_account: FinancialAccount
    ):
        """Test successful transaction deletion"""
        # Create a new transaction to delete
        transaction = Transaction(
            user_id=test_user.id,
            account_id=test_account.id,
            transaction_date=date.today(),
            amount=25.00,
            transaction_type=TransactionType.DEBIT,
            category=TransactionCategory.COFFEE,
            description="To delete"
        )
        db_session.add(transaction)
        await db_session.commit()
        await db_session.refresh(transaction)
        
        response = await client.delete(
            f"/api/v1/transactions/{transaction.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
    
    async def test_delete_nonexistent_transaction(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test deleting non-existent transaction"""
        import uuid
        fake_id = uuid.uuid4()
        response = await client.delete(
            f"/api/v1/transactions/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404


@pytest.mark.financial
@pytest.mark.asyncio
class TestTransactionAnalytics:
    """Test transaction analytics endpoint"""
    
    async def test_get_analytics_default_range(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_transaction: Transaction
    ):
        """Test getting analytics with default date range"""
        response = await client.get(
            "/api/v1/transactions/analytics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_income" in data
        assert "total_expenses" in data
        assert "net_amount" in data
        assert "transaction_count" in data
        assert "spending_by_category" in data
    
    async def test_get_analytics_custom_range(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting analytics with custom date range"""
        start_date = (date.today() - timedelta(days=30)).isoformat()
        end_date = date.today().isoformat()
        
        response = await client.get(
            f"/api/v1/transactions/analytics?start_date={start_date}&end_date={end_date}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["start_date"] == start_date
        assert data["end_date"] == end_date
    
    async def test_analytics_includes_all_metrics(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_transaction: Transaction
    ):
        """Test analytics includes all expected metrics"""
        response = await client.get(
            "/api/v1/transactions/analytics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check all expected fields
        expected_fields = [
            "start_date", "end_date", "transaction_count",
            "total_income", "total_expenses", "net_amount",
            "spending_by_category", "income_by_category",
            "top_merchants", "daily_totals",
            "recurring_count", "recurring_total",
            "avg_transaction_amount", "avg_daily_spending"
        ]
        
        for field in expected_fields:
            assert field in data


@pytest.mark.financial
@pytest.mark.asyncio
class TestBulkCategorize:
    """Test bulk categorization endpoint"""
    
    async def test_bulk_categorize_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User,
        test_account: FinancialAccount
    ):
        """Test successful bulk categorization"""
        # Create multiple transactions
        transactions = []
        for i in range(3):
            txn = Transaction(
                user_id=test_user.id,
                account_id=test_account.id,
                transaction_date=date.today(),
                amount=10.00 * (i + 1),
                transaction_type=TransactionType.DEBIT,
                category=TransactionCategory.UNCATEGORIZED,
                description=f"Transaction {i}"
            )
            transactions.append(txn)
            db_session.add(txn)
        
        await db_session.commit()
        for txn in transactions:
            await db_session.refresh(txn)
        
        # Bulk categorize
        categorize_data = {
            "transaction_ids": [str(txn.id) for txn in transactions],
            "category": "groceries"
        }
        
        response = await client.post(
            "/api/v1/transactions/categorize",
            json=categorize_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["updated_count"] == 3
        assert len(data["failed_ids"]) == 0
    
    async def test_bulk_categorize_partial_failure(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_transaction: Transaction
    ):
        """Test bulk categorization with some invalid IDs"""
        import uuid
        
        categorize_data = {
            "transaction_ids": [
                str(test_transaction.id),
                str(uuid.uuid4()),  # Invalid ID
                str(uuid.uuid4())   # Invalid ID
            ],
            "category": "groceries"
        }
        
        response = await client.post(
            "/api/v1/transactions/categorize",
            json=categorize_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["updated_count"] == 1
        assert len(data["failed_ids"]) == 2


@pytest.mark.financial
@pytest.mark.asyncio
class TestTransactionAuthorization:
    """Test transaction authorization"""
    
    async def test_cannot_access_other_user_transaction(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_account: FinancialAccount
    ):
        """Test that users cannot access other users' transactions"""
        # Create another user
        from app.core.security import get_password_hash, create_access_token
        from app.models.user import User
        
        other_user = User(
            email="other@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Other User",
            is_active=True,
            is_verified=True
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)
        
        # Create transaction for first user
        transaction = Transaction(
            user_id=test_account.user_id,
            account_id=test_account.id,
            transaction_date=date.today(),
            amount=100.00,
            transaction_type=TransactionType.DEBIT,
            category=TransactionCategory.GROCERIES
        )
        db_session.add(transaction)
        await db_session.commit()
        await db_session.refresh(transaction)
        
        # Try to access with other user's token
        other_token = create_access_token(data={"sub": str(other_user.id)})
        other_headers = {"Authorization": f"Bearer {other_token}"}
        
        response = await client.get(
            f"/api/v1/transactions/{transaction.id}",
            headers=other_headers
        )
        
        assert response.status_code == 404


# Made with Bob