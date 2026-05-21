"""
Test Loan and EMI Integration in Calculators
Tests that calculators automatically consider existing loans and EMI obligations
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.models.user import User
from app.models.account import FinancialAccount, AccountType
from app.models.transaction import Transaction, TransactionType, TransactionCategory


@pytest.mark.asyncio
class TestLoanIntegrationInCalculators:
    """Test that calculators consider existing loans and EMI"""
    
    async def test_retirement_calculator_with_loans(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test retirement calculator considers existing loan EMI"""
        # Create a loan account
        loan = FinancialAccount(
            user_id=test_user.id,
            account_type=AccountType.LOAN,
            institution_name="HDFC Bank",
            account_name="Home Loan",
            balance=5000000.00,  # 50 lakh outstanding
            currency="INR",
            loan_principal=5000000.00,
            loan_outstanding=5000000.00,
            interest_rate=8.5,
            emi_amount=40000.00,  # 40k EMI per month
            loan_tenure_months=240,
            remaining_tenure_months=200,
            is_active=True
        )
        db_session.add(loan)
        
        # Create income transactions (salary)
        for i in range(3):
            transaction = Transaction(
                user_id=test_user.id,
                account_id=loan.id,
                transaction_type=TransactionType.CREDIT,
                amount=100000.00,  # 1 lakh salary
                description="Salary Credit",
                transaction_date=datetime.utcnow() - timedelta(days=30 * i),
                category=TransactionCategory.INCOME
            )
            db_session.add(transaction)
        
        # Create expense transactions
        for i in range(3):
            transaction = Transaction(
                user_id=test_user.id,
                account_id=loan.id,
                transaction_type=TransactionType.DEBIT,
                amount=30000.00,  # 30k expenses
                description="Monthly Expenses",
                transaction_date=datetime.utcnow() - timedelta(days=30 * i),
                category=TransactionCategory.SHOPPING
            )
            db_session.add(transaction)
        
        await db_session.commit()
        
        # Run retirement simulation
        params = {
            "current_age": 35,
            "retirement_age": 60,
            "current_savings": 500000,
            "expected_return": 0.10,
            "inflation_rate": 0.06
            # Note: NOT providing monthly_contribution - should be auto-calculated
        }
        
        response = await client.post(
            "/api/v1/simulations/retirement/quick",
            headers=auth_headers,
            json=params
        )
        
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        
        # Verify loan data is included
        assert "loan_obligations" in results
        assert results["loan_obligations"]["total_monthly_emi"] == 40000.00
        assert results["loan_obligations"]["loan_count"] == 1
        
        # Verify spending data shows correct calculations
        spending_data = results.get("spending_data_used", {})
        assert spending_data["monthly_income"] == 100000.00
        assert spending_data["monthly_expenses"] == 30000.00
        assert spending_data["monthly_savings"] == 70000.00  # Before EMI
        assert spending_data["total_monthly_emi"] == 40000.00
        assert spending_data["available_for_investment"] == 30000.00  # After EMI: 70k - 40k
        
        # The monthly_contribution used should be 30k (after EMI), not 70k
        # This ensures realistic retirement planning
    
    async def test_investment_calculator_with_multiple_loans(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test investment calculator with multiple loan EMIs"""
        # Create multiple loans
        loans = [
            FinancialAccount(
                user_id=test_user.id,
                account_type=AccountType.LOAN,
                institution_name="HDFC Bank",
                account_name="Home Loan",
                balance=3000000.00,
                currency="INR",
                loan_principal=3000000.00,
                loan_outstanding=3000000.00,
                interest_rate=8.5,
                emi_amount=25000.00,
                loan_tenure_months=240,
                is_active=True
            ),
            FinancialAccount(
                user_id=test_user.id,
                account_type=AccountType.LOAN,
                institution_name="ICICI Bank",
                account_name="Car Loan",
                balance=500000.00,
                currency="INR",
                loan_principal=500000.00,
                loan_outstanding=500000.00,
                interest_rate=9.5,
                emi_amount=10000.00,
                loan_tenure_months=60,
                is_active=True
            )
        ]
        
        for loan in loans:
            db_session.add(loan)
        
        # Create income transactions
        for i in range(3):
            transaction = Transaction(
                user_id=test_user.id,
                account_id=loans[0].id,
                transaction_type=TransactionType.CREDIT,
                amount=150000.00,  # 1.5 lakh salary
                description="Salary",
                transaction_date=datetime.utcnow() - timedelta(days=30 * i),
                category=TransactionCategory.INCOME
            )
            db_session.add(transaction)
        
        await db_session.commit()
        
        # Run investment simulation
        params = {
            "initial_investment": 100000,
            "years": 10,
            "expected_return": 0.12,
            "risk_level": "moderate"
        }
        
        response = await client.post(
            "/api/v1/simulations/investment/quick",
            headers=auth_headers,
            json=params
        )
        
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        
        # Verify multiple loans are tracked
        assert "loan_obligations" in results
        assert results["loan_obligations"]["total_monthly_emi"] == 35000.00  # 25k + 10k
        assert results["loan_obligations"]["loan_count"] == 2
        assert len(results["loan_obligations"]["loan_accounts"]) == 2
    
    async def test_loan_calculator_with_existing_loan_without_transactions(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test loan calculator considers existing EMI even without transaction history"""
        loan = FinancialAccount(
            user_id=test_user.id,
            account_type=AccountType.LOAN,
            institution_name="HDFC Bank",
            account_name="Home Loan",
            balance=2000000.00,
            currency="INR",
            loan_principal=2500000.00,
            loan_outstanding=2000000.00,
            interest_rate=8.5,
            emi_amount=30000.00,
            loan_tenure_months=240,
            remaining_tenure_months=180,
            is_active=True
        )
        db_session.add(loan)
        await db_session.commit()
        
        params = {
            "loan_amount": 1000000,
            "interest_rate": 0.10,
            "loan_term_years": 10,
            "current_monthly_income": 100000
        }
        
        response = await client.post(
            "/api/v1/simulations/loan-payoff/quick",
            headers=auth_headers,
            json=params
        )
        
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        
        assert results["existing_monthly_emi"] == 30000.00
        assert results["existing_loan_outstanding"] == 2000000.00
        assert results["existing_loan_count"] == 1
        assert results["total_monthly_payment_with_existing_emi"] == (
            results["total_monthly_payment"] + 30000.00
        )
        assert results["combined_loan_principal_with_existing"] == 3000000.00
        assert results["affordability_analysis"]["existing_emi"] == 30000.00
        assert results["affordability_analysis"]["total_emi_burden"] == (
            results["monthly_payment"] + 30000.00
        )
        assert "loan_obligations" in results
        assert results["loan_obligations"]["total_monthly_emi"] == 30000.00
        assert results["loan_obligations"]["total_loan_outstanding"] == 2000000.00
    
    async def test_calculator_without_loans(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test calculator works correctly when user has no loans"""
        # Create only income transactions, no loans
        for i in range(3):
            transaction = Transaction(
                user_id=test_user.id,
                account_id=None,
                transaction_type=TransactionType.CREDIT,
                amount=80000.00,
                description="Salary",
                transaction_date=datetime.utcnow() - timedelta(days=30 * i),
                category=TransactionCategory.INCOME
            )
            db_session.add(transaction)
        
        await db_session.commit()
        
        # Run retirement simulation
        params = {
            "current_age": 30,
            "retirement_age": 60,
            "current_savings": 200000,
            "expected_return": 0.10,
            "inflation_rate": 0.06
        }
        
        response = await client.post(
            "/api/v1/simulations/retirement/quick",
            headers=auth_headers,
            json=params
        )
        
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        
        # Should not have loan_obligations key when no loans
        assert "loan_obligations" not in results
        
        # Spending data should show no EMI
        spending_data = results.get("spending_data_used", {})
        assert spending_data.get("total_monthly_emi", 0) == 0
        assert spending_data.get("monthly_savings") == spending_data.get("available_for_investment")


# Made with Bob
