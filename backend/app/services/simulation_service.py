"""
Simulation Service
Handles financial simulations including retirement planning, investment scenarios,
loan payoff calculations, and budget forecasting
Enhanced with automatic spending data integration from transactions
"""
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from decimal import Decimal

from sqlalchemy import select, and_, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
import numpy as np

from app.models.simulation import FinancialSimulation, SimulationType, SimulationStatus
from app.models.transaction import Transaction, TransactionType
from app.schemas.simulation import (
    SimulationCreate,
    SimulationUpdate,
    SimulationResponse,
    RetirementSimulationParams,
    InvestmentSimulationParams,
    LoanPayoffSimulationParams,
    BudgetForecastParams,
    SavingsGoalParams,
)
from config import settings


class SimulationService:
    """Service for financial simulations and forecasting"""
    
    def __init__(self):
        self.default_inflation_rate = settings.SIMULATION_DEFAULT_INFLATION_RATE
        self.default_return_rate = settings.SIMULATION_DEFAULT_RETURN_RATE
        self.monte_carlo_iterations = settings.SIMULATION_MONTE_CARLO_ITERATIONS
        self.max_years = settings.SIMULATION_MAX_YEARS
    
    async def get_user_spending_data(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        months: int = 6
    ) -> Dict[str, Any]:
        """
        Fetch user's spending data from transactions and loan obligations
        
        Args:
            db: Database session
            user_id: User ID
            months: Number of months to analyze (default: 6)
            
        Returns:
            Dictionary with spending analysis including:
            - monthly_income: Average monthly income
            - monthly_expenses: Average monthly expenses (from debit transactions)
            - monthly_savings: Average monthly savings (after EMI)
            - total_monthly_emi: Total EMI obligations
            - loan_accounts: List of active loans
            - category_breakdown: Spending by category
            - has_data: Whether user has transaction data
        """
        # Calculate date range - using 30-day months
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=months * 30)
        
        # Query transactions
        result = await db.execute(
            select(Transaction).where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date
                )
            )
        )
        transactions = result.scalars().all()
        
        # Import FinancialAccount and AccountType here to avoid circular imports
        from app.models.account import FinancialAccount, AccountType
        
        # Query active loan accounts
        loan_result = await db.execute(
            select(FinancialAccount).where(
                and_(
                    FinancialAccount.user_id == user_id,
                    FinancialAccount.account_type == AccountType.LOAN,
                    FinancialAccount.is_active == True
                )
            )
        )
        loan_accounts = loan_result.scalars().all()
        
        # Calculate total monthly EMI
        total_monthly_emi = sum(
            float(loan.emi_amount) for loan in loan_accounts
            if loan.emi_amount is not None
        )
        total_loan_outstanding = sum(
            float(loan.loan_outstanding or loan.balance or 0) for loan in loan_accounts
        )
        
        # Prepare loan details
        loan_details = []
        for loan in loan_accounts:
            loan_details.append({
                "account_name": loan.account_name or loan.institution_name,
                "outstanding": float(loan.loan_outstanding) if loan.loan_outstanding else 0,
                "emi_amount": float(loan.emi_amount) if loan.emi_amount else 0,
                "interest_rate": float(loan.interest_rate) if loan.interest_rate else 0,
                "remaining_months": loan.remaining_tenure_months or 0
            })
        
        # Query investment accounts for total investment balance
        investment_result = await db.execute(
            select(FinancialAccount).where(
                and_(
                    FinancialAccount.user_id == user_id,
                    FinancialAccount.account_type == AccountType.INVESTMENT,
                    FinancialAccount.is_active == True
                )
            )
        )
        investment_accounts = investment_result.scalars().all()
        
        # Calculate total investment balance
        total_investment_balance = sum(
            float(account.balance) for account in investment_accounts
            if account.balance is not None
        )
        
        if not transactions:
            return {
                "has_data": False,
                "monthly_income": 0,
                "monthly_expenses": 0,
                "monthly_savings": 0,
                "total_monthly_emi": round(total_monthly_emi, 2),
                "total_loan_outstanding": round(total_loan_outstanding, 2),
                "available_for_investment": 0,
                "loan_accounts": loan_details,
                "loan_count": len(loan_accounts),
                "category_breakdown": {},
                "message": "No transaction data available. Please add transactions or provide manual estimates."
            }
        
        # Calculate totals - sum all DEBIT transactions for expenses
        total_income = sum(float(t.amount) for t in transactions if t.transaction_type == TransactionType.CREDIT)
        total_expenses = sum(float(t.amount) for t in transactions if t.transaction_type == TransactionType.DEBIT)
        
        # Category breakdown for expenses
        category_breakdown = {}
        for t in transactions:
            if t.transaction_type == TransactionType.DEBIT and t.category:
                cat = t.category.value
                category_breakdown[cat] = category_breakdown.get(cat, 0) + float(t.amount)
        
        # Calculate monthly averages using 30-day months
        # This gives a more accurate monthly expense by averaging all debit transactions
        # over the specified period (default 6 months = 180 days)
        monthly_income = total_income / months
        monthly_expenses = total_expenses / months  # Average of all debit transactions per 30-day month
        monthly_savings_before_emi = monthly_income - monthly_expenses
        
        # Calculate available for investment (after EMI deduction)
        available_for_investment = max(0, monthly_savings_before_emi - total_monthly_emi)
        
        return {
            "has_data": True,
            "monthly_income": round(monthly_income, 2),
            "monthly_expenses": round(monthly_expenses, 2),
            "monthly_savings": round(monthly_savings_before_emi, 2),
            "total_monthly_emi": round(total_monthly_emi, 2),
            "total_loan_outstanding": round(total_loan_outstanding, 2),
            "available_for_investment": round(available_for_investment, 2),
            "total_investment_balance": round(total_investment_balance, 2),
            "savings_rate": round((monthly_savings_before_emi / monthly_income * 100), 1) if monthly_income > 0 else 0,
            "investment_rate": round((available_for_investment / monthly_income * 100), 1) if monthly_income > 0 else 0,
            "loan_accounts": loan_details,
            "loan_count": len(loan_accounts),
            "category_breakdown": {k: round(v / months, 2) for k, v in category_breakdown.items()},
            "analysis_period_months": months,
            "transaction_count": len(transactions),
            "data_quality": "good" if len(transactions) >= months * 10 else "limited"
        }
    
    async def create_simulation(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        simulation_data: SimulationCreate,
    ) -> FinancialSimulation:
        """
        Create a new financial simulation
        
        Args:
            db: Database session
            user_id: User ID
            simulation_data: Simulation parameters
            
        Returns:
            Created simulation
        """
        simulation = FinancialSimulation(
            user_id=user_id,
            name=simulation_data.name,
            description=simulation_data.description,
            simulation_type=simulation_data.simulation_type,
            parameters=simulation_data.parameters,
            status=SimulationStatus.DRAFT,
        )
        
        db.add(simulation)
        await db.commit()
        await db.refresh(simulation)
        
        return simulation
    
    async def get_simulation(
        self,
        db: AsyncSession,
        simulation_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Optional[FinancialSimulation]:
        """Get a simulation by ID"""
        result = await db.execute(
            select(FinancialSimulation).where(
                and_(
                    FinancialSimulation.id == simulation_id,
                    FinancialSimulation.user_id == user_id,
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def list_simulations(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        simulation_type: Optional[SimulationType] = None,
        status: Optional[SimulationStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FinancialSimulation]:
        """List user's simulations with optional filters"""
        query = select(FinancialSimulation).where(FinancialSimulation.user_id == user_id)
        
        if simulation_type:
            query = query.where(FinancialSimulation.simulation_type == simulation_type)
        
        if status:
            query = query.where(FinancialSimulation.status == status)
        
        query = query.order_by(FinancialSimulation.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def update_simulation(
        self,
        db: AsyncSession,
        simulation_id: uuid.UUID,
        user_id: uuid.UUID,
        update_data: SimulationUpdate,
    ) -> Optional[FinancialSimulation]:
        """Update simulation metadata"""
        simulation = await self.get_simulation(db, simulation_id, user_id)
        if not simulation:
            return None
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(simulation, field, value)
        
        await db.commit()
        await db.refresh(simulation)
        return simulation
    
    async def delete_simulation(
        self,
        db: AsyncSession,
        simulation_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """Delete a simulation"""
        simulation = await self.get_simulation(db, simulation_id, user_id)
        if not simulation:
            return False
        
        await db.delete(simulation)
        await db.commit()
        return True
    
    async def run_simulation(
        self,
        db: AsyncSession,
        simulation_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> FinancialSimulation:
        """
        Execute a financial simulation with automatic spending data integration
        
        Args:
            db: Database session
            simulation_id: Simulation ID
            user_id: User ID
            
        Returns:
            Updated simulation with results
        """
        simulation = await self.get_simulation(db, simulation_id, user_id)
        if not simulation:
            raise HTTPException(status_code=404, detail="Simulation not found")
        
        # Update status
        simulation.status = SimulationStatus.RUNNING
        await db.commit()
        
        try:
            start_time = datetime.utcnow()
            
            # Fetch user's spending data from transactions (with error handling)
            spending_data = {"has_data": False}
            try:
                spending_data = await self.get_user_spending_data(db, user_id)
                print(f"DEBUG: Spending data fetched - Has data: {spending_data.get('has_data')}, EMI: {spending_data.get('total_monthly_emi', 0)}, Loan count: {spending_data.get('loan_count', 0)}")
            except Exception as e:
                # Log error but don't fail the simulation
                print(f"Warning: Could not fetch spending data: {str(e)}")
                import traceback
                traceback.print_exc()
            
            # Merge spending data with simulation parameters
            # User-provided values take precedence over auto-fetched data
            params = simulation.parameters or {}
            enhanced_params: Dict[str, Any] = {}
            
            # Copy existing parameters
            for key, value in params.items():
                enhanced_params[key] = value
            
            # Loan obligations come from account data and should be available even
            # when transaction-based spending history is missing.
            enhanced_params["_total_monthly_emi"] = spending_data.get("total_monthly_emi", 0)
            enhanced_params["_loan_count"] = spending_data.get("loan_count", 0)
            enhanced_params["_has_loans"] = spending_data.get("loan_count", 0) > 0
            enhanced_params["_loan_accounts"] = spending_data.get("loan_accounts", [])
            enhanced_params["_total_loan_outstanding"] = spending_data.get("total_loan_outstanding", 0)
            
            # Add spending data if not already provided by user
            if spending_data.get("has_data", False):
                if "current_monthly_income" not in enhanced_params or enhanced_params.get("current_monthly_income", 0) == 0:
                    enhanced_params["current_monthly_income"] = spending_data["monthly_income"]
                
                if "current_monthly_spending" not in enhanced_params or enhanced_params.get("current_monthly_spending", 0) == 0:
                    enhanced_params["current_monthly_spending"] = spending_data["monthly_expenses"]
                
                if "monthly_contribution" not in enhanced_params or enhanced_params.get("monthly_contribution", 0) == 0:
                    # Use available_for_investment (after EMI deduction) if loans exist
                    # Otherwise use monthly_savings
                    if spending_data.get("total_monthly_emi", 0) > 0:
                        enhanced_params["monthly_contribution"] = spending_data["available_for_investment"]
                    else:
                        enhanced_params["monthly_contribution"] = max(0, spending_data["monthly_savings"])
                
                # Store spending and loan data
                enhanced_params["_spending_data_source"] = "transactions"
                enhanced_params["_spending_data_quality"] = spending_data.get("data_quality", "unknown")
                enhanced_params["_total_investment_balance"] = spending_data.get("total_investment_balance", 0)
            else:
                enhanced_params["_spending_data_source"] = "manual"
            
            # Run appropriate simulation based on type
            sim_type = simulation.simulation_type
            if sim_type == SimulationType.RETIREMENT:
                results = await self._run_retirement_simulation(enhanced_params)
            elif sim_type == SimulationType.INVESTMENT:
                results = await self._run_investment_simulation(enhanced_params)
            elif sim_type == SimulationType.LOAN_PAYOFF:
                results = await self._run_loan_payoff_simulation(enhanced_params)
            elif sim_type == SimulationType.BUDGET_FORECAST:
                results = await self._run_budget_forecast_simulation(enhanced_params)
            elif sim_type == SimulationType.DEBT_REDUCTION:
                results = await self._run_debt_payoff_simulation(enhanced_params)
            elif sim_type == SimulationType.TAX_PLANNING:
                results = await self._run_tax_planning_simulation(enhanced_params)
            elif sim_type == SimulationType.SAVINGS_GOAL:
                results = await self._run_emergency_fund_simulation(enhanced_params)
            elif sim_type == SimulationType.CASH_FLOW:
                results = await self._run_college_savings_simulation(enhanced_params)
            elif sim_type == SimulationType.NET_WORTH:
                results = await self._run_net_worth_simulation(enhanced_params)
            elif sim_type == SimulationType.WHAT_IF:
                results = await self._run_real_estate_simulation(enhanced_params)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported simulation type: {sim_type}")
            
            # Add spending data and loan info to results
            if spending_data.get("has_data", False):
                # Use manually entered income if provided, otherwise use transaction-based
                actual_monthly_income = enhanced_params.get("current_monthly_income", spending_data.get("monthly_income", 0))
                actual_monthly_expenses = spending_data.get("monthly_expenses", 0)
                actual_monthly_savings = actual_monthly_income - actual_monthly_expenses
                actual_available_for_investment = max(0, actual_monthly_savings - spending_data.get("total_monthly_emi", 0))
                
                results["spending_data_used"] = {
                    "monthly_income": actual_monthly_income,
                    "monthly_expenses": actual_monthly_expenses,
                    "monthly_savings": actual_monthly_savings,
                    "total_monthly_emi": spending_data.get("total_monthly_emi", 0),
                    "available_for_investment": actual_available_for_investment,
                    "savings_rate": round((actual_monthly_savings / actual_monthly_income * 100), 1) if actual_monthly_income > 0 else 0,
                    "investment_rate": round((actual_available_for_investment / actual_monthly_income * 100), 1) if actual_monthly_income > 0 else 0,
                    "data_source": "manual_income" if enhanced_params.get("current_monthly_income", 0) > 0 else "transactions",
                    "analysis_period_months": spending_data.get("analysis_period_months", 0),
                    "transaction_count": spending_data.get("transaction_count", 0),
                    "data_quality": spending_data.get("data_quality", "unknown"),
                    "total_investment_balance": spending_data.get("total_investment_balance", 0)
                }
                
            
            # Add loan information if loans exist, even without transaction history.
            if spending_data.get("loan_count", 0) > 0:
                results["loan_obligations"] = {
                    "total_monthly_emi": spending_data.get("total_monthly_emi", 0),
                    "total_loan_outstanding": spending_data.get("total_loan_outstanding", 0),
                    "loan_count": spending_data.get("loan_count", 0),
                    "loan_accounts": spending_data.get("loan_accounts", []),
                    "impact_on_savings": spending_data.get("monthly_savings", 0) - spending_data.get("available_for_investment", 0)
                }
            
            end_time = datetime.utcnow()
            execution_time = int((end_time - start_time).total_seconds())
            
            # Update simulation with results
            simulation.results = results
            simulation.status = SimulationStatus.COMPLETED
            simulation.executed_at = end_time
            simulation.execution_time_ms = execution_time * 1000
            
            await db.commit()
            await db.refresh(simulation)
            
            return simulation
            
        except Exception as e:
            simulation.status = SimulationStatus.FAILED
            simulation.error_message = str(e)
            await db.commit()
            raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")
    
    async def _run_retirement_simulation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run retirement planning simulation
        
        Uses 4% Safe Withdrawal Rule for required corpus calculation.
        
        Calculates:
        - Required savings (using safe withdrawal rate)
        - Monthly contributions needed
        - Projected retirement income
        - Probability of success (Monte Carlo)
        """
        current_age = params.get('current_age', 30)
        retirement_age = params.get('retirement_age', 65)
        life_expectancy = params.get('life_expectancy', 90)
        
        # Use investment account balance if current_savings is 0 or not provided
        current_savings = params.get('current_savings', 0)
        if current_savings == 0 or current_savings is None:
            current_savings = params.get('_total_investment_balance', 0)
        
        monthly_contribution = params.get('monthly_contribution', 0)
        annual_return = params.get('annual_return', self.default_return_rate)
        inflation_rate = params.get('inflation_rate', self.default_inflation_rate)
        
        # Calculate desired annual income from monthly income if provided
        # Otherwise use default of 50000
        monthly_income = params.get('current_monthly_income', 0)
        monthly_emi = params.get('_total_monthly_emi', 0)
        
        if monthly_income > 0:
            # Check if user has loans that will be paid off before retirement
            # If loans exist, retirement income needs will be higher (no EMI to pay)
            # We assume most loans (home, car) will be paid off before retirement
            
            # Calculate net income after EMI for current lifestyle
            net_monthly_income = monthly_income - monthly_emi
            
            # In retirement, assuming loans are paid off, user will have full income available
            # So we use 80% of GROSS income (not net after EMI)
            # This is because EMI obligations typically end before retirement
            desired_annual_income = monthly_income * 12 * 0.8
            
            # Store for display purposes
            params['_retirement_income_assumption'] = f"Assumes loans paid off before retirement. Based on 80% of ₹{monthly_income:,.0f}/month"
        else:
            desired_annual_income = params.get('desired_annual_income', 50000)
        
        withdrawal_rate = params.get('withdrawal_rate', 0.04)  # 4% safe withdrawal rule
        
        # Input validation
        if retirement_age <= current_age:
            raise ValueError("Retirement age must be greater than current age")
        if life_expectancy <= retirement_age:
            raise ValueError("Life expectancy must be greater than retirement age")
        if current_savings < 0 or monthly_contribution < 0:
            raise ValueError("Savings and contributions must be non-negative")
        
        years_to_retirement = retirement_age - current_age
        years_in_retirement = life_expectancy - retirement_age
        
        # Calculate future value of current savings
        fv_current = current_savings * ((1 + annual_return) ** years_to_retirement)
        
        # Calculate future value of monthly contributions (end-of-month contributions)
        monthly_rate = annual_return / 12
        months_to_retirement = years_to_retirement * 12
        if monthly_rate > 0:
            fv_contributions = monthly_contribution * (((1 + monthly_rate) ** months_to_retirement - 1) / monthly_rate)
        else:
            fv_contributions = monthly_contribution * months_to_retirement
        
        total_at_retirement = fv_current + fv_contributions
        
        # Calculate required corpus using 4% Safe Withdrawal Rule
        # Adjust desired income for inflation at retirement
        inflation_adjusted_income = desired_annual_income * ((1 + inflation_rate) ** years_to_retirement)
        
        # Required corpus = Annual expenses / Safe withdrawal rate
        required_savings = inflation_adjusted_income / withdrawal_rate
        
        # Calculate shortfall/surplus
        shortfall = required_savings - total_at_retirement
        
        # Calculate required monthly contribution to meet goal
        if shortfall > 0 and monthly_rate > 0:
            required_monthly = (required_savings - fv_current) * monthly_rate / ((1 + monthly_rate) ** months_to_retirement - 1)
        else:
            required_monthly = 0
        
        # Monte Carlo simulation for success probability
        risk_level = params.get('risk_level', 'moderate')
        success_rate = await self._monte_carlo_retirement(
            current_savings, monthly_contribution, years_to_retirement,
            years_in_retirement, annual_return, inflation_rate, desired_annual_income,
            risk_level
        )
        
        return {
            "current_age": current_age,
            "retirement_age": retirement_age,
            "years_to_retirement": years_to_retirement,
            "years_in_retirement": years_in_retirement,
            "current_savings": current_savings,
            "monthly_contribution": monthly_contribution,
            "projected_savings_at_retirement": round(total_at_retirement, 2),
            "required_savings": round(required_savings, 2),
            "shortfall": round(shortfall, 2) if shortfall > 0 else 0,
            "surplus": round(abs(shortfall), 2) if shortfall < 0 else 0,
            "required_monthly_contribution": round(required_monthly, 2),
            "success_probability": round(success_rate * 100, 1),
            "inflation_adjusted_annual_income": round(inflation_adjusted_income, 2),
            "withdrawal_rate_used": withdrawal_rate,
            "assumptions": {
                "annual_return": annual_return,
                "inflation_rate": inflation_rate,
                "life_expectancy": life_expectancy,
                "safe_withdrawal_rate": withdrawal_rate,
                "contribution_timing": "end_of_month",
            },
            "disclaimer": "Projections use the 4% Safe Withdrawal Rule and simplified normal distribution for returns. Actual results may vary significantly due to market volatility, sequence of returns risk, and other factors not captured in this model."
        }
    
    async def _monte_carlo_retirement(
        self, current_savings: float, monthly_contribution: float,
        years_to_retirement: int, years_in_retirement: int,
        mean_return: float, inflation_rate: float, desired_income: float,
        risk_level: str = 'moderate'
    ) -> float:
        """Run Monte Carlo simulation for retirement success probability"""
        iterations = min(self.monte_carlo_iterations, 1000)
        successes = 0
        
        # Map risk level to volatility
        volatility_map = {
            'conservative': 0.08,
            'moderate': 0.15,
            'aggressive': 0.25
        }
        std_dev = volatility_map.get(risk_level, 0.15)
        
        for _ in range(iterations):
            # Simulate accumulation phase
            balance = current_savings
            for year in range(years_to_retirement):
                annual_return = np.random.normal(mean_return, std_dev)
                balance = balance * (1 + annual_return) + (monthly_contribution * 12)
            
            # Simulate withdrawal phase
            inflation_adjusted_income = desired_income * ((1 + inflation_rate) ** years_to_retirement)
            for year in range(years_in_retirement):
                annual_return = np.random.normal(mean_return, std_dev)
                balance = balance * (1 + annual_return) - inflation_adjusted_income
                inflation_adjusted_income *= (1 + inflation_rate)
                
                if balance <= 0:
                    break
            
            if balance > 0:
                successes += 1
        
        return successes / iterations
    
    async def _run_investment_simulation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run investment scenario simulation with risk analysis"""
        initial_investment = params.get('initial_investment', 10000)
        monthly_contribution = params.get('monthly_contribution', 500)
        years = params.get('years', 10)
        expected_return = params.get('expected_return', self.default_return_rate)
        risk_level = params.get('risk_level', 'moderate')
        
        # Input validation
        if initial_investment < 0 or monthly_contribution < 0:
            raise ValueError("Investment amounts must be non-negative")
        if years <= 0:
            raise ValueError("Investment period must be positive")
        if expected_return < -1:  # Allow negative returns but not less than -100%
            raise ValueError("Expected return must be greater than -100%")
        
        # Configurable volatility based on risk level
        volatility_map = {
            'conservative': 0.08,
            'moderate': 0.15,
            'aggressive': 0.25
        }
        volatility = volatility_map.get(risk_level, 0.15)
        
        # Calculate deterministic projection
        monthly_rate = expected_return / 12
        months = years * 12
        
        fv_initial = initial_investment * ((1 + expected_return) ** years)
        if monthly_rate > 0:
            fv_contributions = monthly_contribution * (((1 + monthly_rate) ** months - 1) / monthly_rate)
        else:
            fv_contributions = monthly_contribution * months
        
        expected_value = fv_initial + fv_contributions
        
        # Run Monte Carlo for scenarios
        scenarios = await self._monte_carlo_investment(
            initial_investment, monthly_contribution, years, expected_return, volatility
        )
        
        return {
            "initial_investment": initial_investment,
            "monthly_contribution": monthly_contribution,
            "investment_period_years": years,
            "expected_annual_return": expected_return,
            "risk_level": risk_level,
            "expected_final_value": round(expected_value, 2),
            "best_case_scenario": round(scenarios['best'], 2),
            "worst_case_scenario": round(scenarios['worst'], 2),
            "median_scenario": round(scenarios['median'], 2),
            "total_contributions": initial_investment + (monthly_contribution * months),
            "total_gains": round(expected_value - initial_investment - (monthly_contribution * months), 2),
            "volatility_used": volatility,
            "assumptions": {
                "contribution_timing": "end_of_month",
                "volatility": volatility,
                "risk_level": risk_level,
            },
            "disclaimer": "Market returns are modeled using a simplified normal distribution and do not fully capture extreme market crashes or tail risk. Actual investment returns may vary significantly."
        }
    
    async def _monte_carlo_investment(
        self, initial: float, monthly: float, years: int, mean_return: float, volatility: float
    ) -> Dict[str, float]:
        """Run Monte Carlo simulation for investment scenarios"""
        iterations = min(self.monte_carlo_iterations, 1000)
        final_values = []
        
        for _ in range(iterations):
            balance = initial
            for year in range(years):
                annual_return = np.random.normal(mean_return, volatility)
                balance = balance * (1 + annual_return) + (monthly * 12)
            final_values.append(balance)
        
        final_values.sort()
        return {
            'best': final_values[int(iterations * 0.95)],  # 95th percentile
            'worst': final_values[int(iterations * 0.05)],  # 5th percentile
            'median': final_values[int(iterations * 0.50)],  # 50th percentile
        }
    
    async def _run_loan_payoff_simulation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run loan payoff simulation with amortization and affordability analysis
        
        Considers user's income to recommend optimal loan tenure
        """
        loan_amount = params.get('loan_amount', 100000)
        interest_rate = params.get('interest_rate', 0.05)
        loan_term_years = params.get('loan_term_years', 30)
        extra_payment = params.get('extra_payment', 0)
        
        # Get income data for affordability analysis
        monthly_income = params.get('current_monthly_income', 0)
        monthly_expenses = params.get('current_monthly_spending', 0)
        existing_emi = params.get('_total_monthly_emi', 0)
        existing_loan_outstanding = params.get('_total_loan_outstanding', 0)
        existing_loan_count = params.get('_loan_count', 0)
        
        # Debug logging
        print(f"DEBUG LOAN CALC - Params keys: {list(params.keys())}")
        print(f"DEBUG LOAN CALC - _total_monthly_emi: {params.get('_total_monthly_emi', 'NOT FOUND')}")
        print(f"DEBUG LOAN CALC - existing_emi value: {existing_emi}")
        print(f"DEBUG LOAN CALC - _has_loans: {params.get('_has_loans', 'NOT FOUND')}")
        print(f"DEBUG LOAN CALC - _loan_count: {params.get('_loan_count', 'NOT FOUND')}")
        
        # Input validation
        if loan_amount <= 0:
            raise ValueError("Loan amount must be positive")
        if interest_rate < 0:
            raise ValueError("Interest rate cannot be negative")
        if loan_term_years <= 0:
            raise ValueError("Loan term must be positive")
        if extra_payment < 0:
            raise ValueError("Extra payment cannot be negative")
        
        monthly_rate = interest_rate / 12
        months = loan_term_years * 12
        
        # Calculate standard monthly payment
        if monthly_rate > 0:
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
        else:
            monthly_payment = loan_amount / months
        
        # Treat the loan payment burden as the base payment plus any extra payment
        new_monthly_payment = monthly_payment + extra_payment

        # Calculate payoff with extra payments
        balance = loan_amount
        total_interest = 0
        months_to_payoff = 0

        while balance > 0 and months_to_payoff < months:
            interest_payment = balance * monthly_rate
            principal_payment = new_monthly_payment - interest_payment

            if principal_payment > balance:
                principal_payment = balance

            balance -= principal_payment
            total_interest += interest_payment
            months_to_payoff += 1

        # Calculate interest without extra payments (standard scenario)
        balance_standard = loan_amount
        total_interest_standard = 0
        for month in range(months):
            interest_payment_standard = balance_standard * monthly_rate
            principal_payment_standard = monthly_payment - interest_payment_standard
            if principal_payment_standard > balance_standard:
                principal_payment_standard = balance_standard
            balance_standard -= principal_payment_standard
            total_interest_standard += interest_payment_standard
            if balance_standard <= 0:
                break
        
        years_saved = (months - months_to_payoff) / 12
        interest_saved = total_interest_standard - total_interest
        
        result = {
            "loan_amount": loan_amount,
            "interest_rate": interest_rate,
            "original_term_years": loan_term_years,
            "monthly_payment": round(monthly_payment, 2),
            "extra_monthly_payment": extra_payment,
            "new_monthly_payment": round(new_monthly_payment, 2),
            "total_monthly_payment": round(new_monthly_payment, 2),
            "existing_monthly_emi": round(existing_emi, 2),
            "existing_loan_outstanding": round(existing_loan_outstanding, 2),
            "existing_loan_count": existing_loan_count,
            "total_monthly_payment_with_existing_emi": round(new_monthly_payment + existing_emi, 2),
            "combined_loan_principal_with_existing": round(loan_amount + existing_loan_outstanding, 2),
            "months_to_payoff": months_to_payoff,
            "years_to_payoff": round(months_to_payoff / 12, 1),
            "years_saved": round(years_saved, 1),
            "total_interest_paid": round(total_interest, 2),
            "interest_saved": round(interest_saved, 2) if interest_saved > 0 else 0,
            "total_amount_paid": round(loan_amount + total_interest, 2),
        }
        
        # Add affordability analysis if income data is available
        if monthly_income > 0:
            # Calculate total EMI burden (new loan payment including extra payment + existing loans)
            total_emi_burden = new_monthly_payment + existing_emi
            emi_to_income_ratio = (total_emi_burden / monthly_income) * 100
            
            # Calculate available income after all EMIs
            available_after_all_emis = monthly_income - total_emi_burden
            
            result["affordability_analysis"] = {
                "monthly_income": round(monthly_income, 2),
                "monthly_expenses": round(monthly_expenses, 2),
                "existing_emi": round(existing_emi, 2),
                "new_emi": round(new_monthly_payment, 2),
                "total_emi_burden": round(total_emi_burden, 2),
                "emi_to_income_ratio": round(emi_to_income_ratio, 1),
                "available_income_after_emi": round(available_after_all_emis, 2),
                "is_affordable": emi_to_income_ratio <= 50,  # Standard: EMI should not exceed 50% of income
                "affordability_status": self._get_affordability_status(emi_to_income_ratio),
                "has_existing_loans": existing_emi > 0,
                "existing_loan_count": existing_loan_count,
                "existing_loan_outstanding": round(existing_loan_outstanding, 2)
            }
            
            # Calculate recommended loan tenure for better affordability
            if emi_to_income_ratio > 40:  # If EMI burden is high
                recommended_emi = monthly_income * 0.35  # Target 35% of income
                if recommended_emi > existing_emi:
                    safe_emi = recommended_emi - existing_emi
                    
                    # Calculate tenure needed for safe EMI
                    if monthly_rate > 0 and safe_emi > 0:
                        # Using loan formula: EMI = P * [r(1+r)^n] / [(1+r)^n - 1]
                        # Solving for n (months)
                        temp = safe_emi / (loan_amount * monthly_rate)
                        if temp > 1:
                            recommended_months = round(np.log(temp / (temp - 1)) / np.log(1 + monthly_rate))
                            recommended_years = round(recommended_months / 12, 1)
                            
                            # Calculate interest for recommended tenure
                            if monthly_rate > 0:
                                recommended_monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** recommended_months) / ((1 + monthly_rate) ** recommended_months - 1)
                            else:
                                recommended_monthly_payment = loan_amount / recommended_months
                            
                            recommended_total_interest = (recommended_monthly_payment * recommended_months) - loan_amount
                            
                            result["affordability_analysis"]["recommendation"] = {
                                "recommended_tenure_years": recommended_years,
                                "recommended_emi": round(safe_emi, 2),
                                "recommended_total_interest": round(recommended_total_interest, 2),
                                "emi_reduction": round(monthly_payment - safe_emi, 2),
                                "additional_interest_cost": round(recommended_total_interest - total_interest, 2),
                                "message": f"Consider extending tenure to {recommended_years} years for better affordability"
                            }
        
        return result
    
    def _get_affordability_status(self, emi_ratio: float) -> str:
        """Get affordability status based on EMI to income ratio"""
        if emi_ratio <= 30:
            return "Excellent - Very comfortable EMI burden"
        elif emi_ratio <= 40:
            return "Good - Manageable EMI burden"
        elif emi_ratio <= 50:
            return "Moderate - EMI burden is at upper limit"
        elif emi_ratio <= 60:
            return "High - EMI burden may strain finances"
        else:
            return "Very High - EMI burden is unsustainable"
    
    async def _run_budget_forecast_simulation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run budget forecast simulation with growth projections"""
        monthly_income = params.get('monthly_income', 5000)
        monthly_expenses = params.get('monthly_expenses', 4000)
        forecast_months = params.get('forecast_months', 12)
        income_growth_rate = params.get('income_growth_rate', 0.03)
        expense_growth_rate = params.get('expense_growth_rate', self.default_inflation_rate)
        
        # Input validation
        if monthly_income < 0 or monthly_expenses < 0:
            raise ValueError("Income and expenses must be non-negative")
        if forecast_months <= 0:
            raise ValueError("Forecast period must be positive")
        
        monthly_savings = monthly_income - monthly_expenses
        
        # Project forward
        projections = []
        cumulative_savings = 0
        current_income = monthly_income
        current_expenses = monthly_expenses
        
        for month in range(1, forecast_months + 1):
            if month % 12 == 0:  # Annual adjustments
                current_income *= (1 + income_growth_rate)
                current_expenses *= (1 + expense_growth_rate)
            
            monthly_net = current_income - current_expenses
            cumulative_savings += monthly_net
            
            projections.append({
                "month": month,
                "income": round(current_income, 2),
                "expenses": round(current_expenses, 2),
                "net_savings": round(monthly_net, 2),
                "cumulative_savings": round(cumulative_savings, 2),
            })
        
        return {
            "starting_monthly_income": monthly_income,
            "starting_monthly_expenses": monthly_expenses,
            "starting_monthly_savings": round(monthly_savings, 2),
            "forecast_period_months": forecast_months,
            "projected_total_savings": round(cumulative_savings, 2),
            "average_monthly_savings": round(cumulative_savings / forecast_months, 2),
            "income_growth_rate": income_growth_rate,
            "expense_growth_rate": expense_growth_rate,
            "monthly_projections": projections,
        }
    
    async def _run_debt_payoff_simulation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run debt payoff simulation (placeholder)"""
        return {"message": "Debt payoff simulation - implementation pending"}
    
    async def _run_tax_planning_simulation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run tax planning simulation (placeholder)"""
        return {"message": "Tax planning simulation - implementation pending"}
    
    async def _run_emergency_fund_simulation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run emergency fund simulation (placeholder)"""
        return {"message": "Emergency fund simulation - implementation pending"}
    
    async def _run_college_savings_simulation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run college savings simulation (placeholder)"""
        return {"message": "College savings simulation - implementation pending"}
    
    async def _run_real_estate_simulation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run real estate purchase simulation (placeholder)"""
        return {"message": "Real estate simulation - implementation pending"}
    
    async def _run_net_worth_simulation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run net worth projection simulation (placeholder)"""
        return {"message": "Net worth projection - implementation pending"}


# Singleton instance
simulation_service = SimulationService()

# Made with Bob
