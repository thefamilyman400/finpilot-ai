"""
Comprehensive Calculation Tests
Tests for all financial calculations including loan interest, EMI, net worth, etc.
"""
import pytest
from decimal import Decimal
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.account import FinancialAccount, AccountType


@pytest.mark.asyncio
class TestLoanCalculations:
    """Test loan-related calculations"""
    
    async def test_loan_emi_calculation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test EMI calculation for loan accounts"""
        # Test case: ₹500,000 loan at 10% for 5 years
        # Expected EMI: ₹10,624.33
        loan_data = {
            "account_type": "loan",
            "institution_name": "HDFC Bank",
            "account_name": "Home Loan",
            "balance": 500000.00,
            "currency": "INR",
            "loan_principal": 500000.00,
            "loan_outstanding": 500000.00,
            "interest_rate": 10.0,
            "loan_tenure_months": 60,
            "emi_amount": 10624.33
        }
        
        response = await client.post(
            "/api/v1/accounts",
            json=loan_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify EMI calculation
        assert abs(data["emi_amount"] - 10624.33) < 1.0  # Allow small rounding difference
        
        # Calculate total interest
        total_payment = data["emi_amount"] * 60
        total_interest = total_payment - 500000
        
        # Expected total interest: ₹137,459.80
        assert abs(total_interest - 137459.80) < 100.0  # Allow reasonable tolerance
    
    async def test_loan_payoff_simulation_accuracy(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test loan payoff simulation with accurate interest calculation"""
        # Test case: $250,000 loan at 4% for 30 years
        params = {
            "loan_amount": 250000,
            "interest_rate": 0.04,  # 4% annual
            "loan_term_years": 30,
            "extra_payment": 0
        }
        
        response = await client.post(
            "/api/v1/simulations/loan-payoff/quick",
            headers=auth_headers,
            json=params
        )
        
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        
        # Verify monthly payment calculation
        # Formula: P * [r(1+r)^n] / [(1+r)^n - 1]
        # Expected: ~$1,193.54
        assert abs(results["monthly_payment"] - 1193.54) < 1.0
        
        # Verify total interest paid
        # Expected: ~$179,673.77
        expected_total_interest = 179673.77
        assert abs(results["total_interest_paid"] - expected_total_interest) < 100.0
        
        # Verify total amount paid
        expected_total = 250000 + expected_total_interest
        assert abs(results["total_amount_paid"] - expected_total) < 100.0
    
    async def test_loan_with_extra_payments(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test loan payoff with extra monthly payments"""
        params = {
            "loan_amount": 200000,
            "interest_rate": 0.05,  # 5% annual
            "loan_term_years": 30,
            "extra_payment": 200
        }
        
        response = await client.post(
            "/api/v1/simulations/loan-payoff/quick",
            headers=auth_headers,
            json=params
        )
        
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        
        # With extra payments, should pay off faster
        assert results["months_to_payoff"] < 360  # Less than 30 years
        assert results["years_saved"] > 0
        assert results["interest_saved"] > 0
        
        # Verify extra payment is included in the outgoing EMI burden
        assert results["affordability_analysis"]["new_emi"] == round(results["monthly_payment"] + params["extra_payment"], 2)
        assert results["affordability_analysis"]["total_emi_burden"] == round(results["monthly_payment"] + params["extra_payment"], 2)
        
        # Total interest should be less than without extra payments
        assert results["total_interest_paid"] < 186511.57  # Standard 30-year interest


@pytest.mark.asyncio
class TestNetWorthCalculations:
    """Test net worth and balance categorization"""
    
    async def test_assets_calculation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test that assets are calculated correctly"""
        # Create various asset accounts
        accounts = [
            FinancialAccount(
                user_id=test_user.id,
                account_type=AccountType.CURRENT,
                institution_name="Bank A",
                account_name="Current Account",
                balance=50000.00,
                currency="INR"
            ),
            FinancialAccount(
                user_id=test_user.id,
                account_type=AccountType.SAVINGS,
                institution_name="Bank B",
                account_name="Savings",
                balance=100000.00,
                currency="INR"
            ),
            FinancialAccount(
                user_id=test_user.id,
                account_type=AccountType.INVESTMENT,
                institution_name="Broker",
                account_name="Stocks",
                balance=200000.00,
                currency="INR"
            ),
        ]
        
        for account in accounts:
            db_session.add(account)
        await db_session.commit()
        
        # Get summary
        response = await client.get(
            "/api/v1/accounts/summary",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Total assets should be sum of all asset accounts
        expected_assets = 350000.00
        assert abs(data["total_assets"] - expected_assets) < 0.01
    
    async def test_liabilities_calculation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test that liabilities are calculated correctly"""
        # Create liability accounts
        accounts = [
            FinancialAccount(
                user_id=test_user.id,
                account_type=AccountType.LOAN,
                institution_name="Bank",
                account_name="Home Loan",
                balance=500000.00,  # Outstanding balance
                currency="INR",
                loan_principal=500000.00,
                loan_outstanding=500000.00,
                interest_rate=8.5,
                loan_tenure_months=240
            ),
            FinancialAccount(
                user_id=test_user.id,
                account_type=AccountType.CREDIT_CARD,
                institution_name="Card Co",
                account_name="Credit Card",
                balance=-25000.00,  # Negative = owed
                currency="INR"
            ),
        ]
        
        for account in accounts:
            db_session.add(account)
        await db_session.commit()
        
        # Get summary
        response = await client.get(
            "/api/v1/accounts/summary",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Total liabilities should be sum of loan balance + credit card debt
        expected_liabilities = 525000.00
        assert abs(data["total_liabilities"] - expected_liabilities) < 0.01
    
    async def test_net_worth_calculation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test net worth = assets - liabilities"""
        # Create mixed accounts
        accounts = [
            # Assets
            FinancialAccount(
                user_id=test_user.id,
                account_type=AccountType.SAVINGS,
                institution_name="Bank",
                account_name="Savings",
                balance=200000.00,
                currency="INR"
            ),
            # Liabilities
            FinancialAccount(
                user_id=test_user.id,
                account_type=AccountType.LOAN,
                institution_name="Bank",
                account_name="Car Loan",
                balance=150000.00,
                currency="INR",
                loan_principal=150000.00,
                loan_outstanding=150000.00,
                interest_rate=9.0,
                loan_tenure_months=60
            ),
        ]
        
        for account in accounts:
            db_session.add(account)
        await db_session.commit()
        
        # Get summary
        response = await client.get(
            "/api/v1/accounts/summary",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Net worth = 200,000 - 150,000 = 50,000
        expected_net_worth = 50000.00
        assert abs(data["net_worth"] - expected_net_worth) < 0.01


@pytest.mark.asyncio
class TestInvestmentCalculations:
    """Test investment growth calculations"""
    
    async def test_investment_simulation_compound_interest(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test investment simulation with compound interest"""
        params = {
            "initial_investment": 100000,
            "monthly_contribution": 5000,
            "years": 10,
            "expected_return": 0.12,  # 12% annual
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
        
        # Verify expected value is calculated
        assert "expected_final_value" in results
        assert results["expected_final_value"] > 100000  # Should grow
        
        # Total contributions = initial + (monthly * months)
        expected_contributions = 100000 + (5000 * 120)
        assert results["total_contributions"] == expected_contributions
        
        # Gains should be positive
        assert results["total_gains"] > 0
        
        # Final value should be greater than contributions (due to returns)
        assert results["expected_final_value"] > expected_contributions


@pytest.mark.asyncio
class TestRetirementCalculations:
    """Test retirement planning calculations"""
    
    async def test_retirement_simulation_future_value(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test retirement simulation future value calculation"""
        params = {
            "current_age": 30,
            "retirement_age": 60,
            "current_savings": 500000,
            "monthly_contribution": 10000,
            "expected_return": 0.10,  # 10% annual
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
        
        # Verify key calculations
        assert results["years_to_retirement"] == 30
        assert results["projected_savings_at_retirement"] > 500000
        assert "required_savings" in results
        assert "success_probability" in results

    async def test_retirement_simulation_includes_existing_investment_accounts(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User
    ):
        """Retirement planning should include the user's investment account balance."""
        investment_account = FinancialAccount(
            user_id=test_user.id,
            account_type=AccountType.INVESTMENT,
            institution_name="Brokerage",
            account_name="Equity Portfolio",
            balance=300000.00,
            currency="INR"
        )
        db_session.add(investment_account)
        await db_session.commit()

        params = {
            "current_age": 30,
            "retirement_age": 60,
            "current_savings": 50000,
            "monthly_contribution": 10000,
            "expected_return": 0.10,
            "inflation_rate": 0.06,
            "current_monthly_income": 100000
        }

        response = await client.post(
            "/api/v1/simulations/retirement/quick",
            headers=auth_headers,
            json=params
        )

        assert response.status_code == 200
        data = response.json()
        results = data["results"]

        assert abs(results["current_investment_balance"] - 300000.00) < 0.01
        assert abs(results["current_savings"] - 350000.00) < 0.01
        assert results["projected_savings_at_retirement"] > 350000.00


@pytest.mark.asyncio
class TestBudgetCalculations:
    """Test budget and cash flow calculations"""
    
    async def test_budget_forecast_projections(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test budget forecast with income/expense growth"""
        params = {
            "monthly_income": 100000,
            "monthly_expenses": 70000,
            "forecast_months": 12,
            "income_growth_rate": 0.10,  # 10% annual
            "expense_growth_rate": 0.06  # 6% annual
        }
        
        response = await client.post(
            "/api/v1/simulations/budget-forecast/quick",
            headers=auth_headers,
            json=params
        )
        
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        
        # Verify starting values
        assert results["starting_monthly_income"] == 100000
        assert results["starting_monthly_expenses"] == 70000
        assert results["starting_monthly_savings"] == 30000
        
        # Verify projections exist
        assert "monthly_projections" in results
        assert len(results["monthly_projections"]) == 12
        
        # Verify cumulative savings is positive
        assert results["projected_total_savings"] > 0


@pytest.mark.asyncio
class TestAccountBalanceCalculations:
    """Test account balance updates and calculations"""
    
    async def test_loan_outstanding_balance_update(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test updating loan outstanding balance"""
        # Create loan account
        loan = FinancialAccount(
            user_id=test_user.id,
            account_type=AccountType.LOAN,
            institution_name="Bank",
            account_name="Personal Loan",
            balance=300000.00,
            currency="INR",
            loan_principal=300000.00,
            loan_outstanding=300000.00,
            interest_rate=11.0,
            loan_tenure_months=36,
            emi_amount=9847.00
        )
        db_session.add(loan)
        await db_session.commit()
        await db_session.refresh(loan)
        
        # Update outstanding balance after payment
        update_data = {
            "balance": 290000.00  # After one EMI payment
        }
        
        response = await client.put(
            f"/api/v1/accounts/{loan.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["balance"] == 290000.00
    
    async def test_credit_card_balance_negative(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test credit card with negative balance (owed amount)"""
        card_data = {
            "account_type": "credit_card",
            "institution_name": "ICICI Bank",
            "account_name": "Credit Card",
            "balance": -15000.00,  # Negative = owed
            "currency": "INR"
        }
        
        response = await client.post(
            "/api/v1/accounts",
            json=card_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["balance"] == -15000.00


@pytest.mark.asyncio
class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    async def test_zero_interest_loan(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test loan with 0% interest"""
        params = {
            "loan_amount": 100000,
            "interest_rate": 0.0,
            "loan_term_years": 5,
            "extra_payment": 0
        }
        
        response = await client.post(
            "/api/v1/simulations/loan-payoff/quick",
            headers=auth_headers,
            json=params
        )
        
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        
        # With 0% interest, total interest should be 0
        assert results["total_interest_paid"] == 0
        # Monthly payment should be principal / months
        expected_payment = 100000 / 60
        assert abs(results["monthly_payment"] - expected_payment) < 0.01
    
    async def test_very_high_interest_rate(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test loan with very high interest rate"""
        params = {
            "loan_amount": 50000,
            "interest_rate": 0.24,  # 24% annual (credit card rate)
            "loan_term_years": 2,
            "extra_payment": 0
        }
        
        response = await client.post(
            "/api/v1/simulations/loan-payoff/quick",
            headers=auth_headers,
            json=params
        )
        
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        
        # High interest means high total interest paid
        assert results["total_interest_paid"] > 10000
        assert results["total_amount_paid"] > 60000


# Made with Bob