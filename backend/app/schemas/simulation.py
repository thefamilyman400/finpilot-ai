"""
Pydantic schemas for financial simulations and scenario planning
"""
from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import UUID


class SimulationTypeEnum(str, Enum):
    """Simulation type enumeration"""
    RETIREMENT = "retirement"
    INVESTMENT = "investment"
    LOAN_PAYOFF = "loan_payoff"
    BUDGET_FORECAST = "budget_forecast"
    SAVINGS_GOAL = "savings_goal"
    DEBT_REDUCTION = "debt_reduction"
    NET_WORTH = "net_worth"
    CASH_FLOW = "cash_flow"
    TAX_PLANNING = "tax_planning"
    WHAT_IF = "what_if"


class SimulationStatusEnum(str, Enum):
    """Simulation execution status"""
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


# Base schemas
class SimulationBase(BaseModel):
    """Base simulation schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    simulation_type: SimulationTypeEnum
    time_horizon_years: int = Field(default=30, ge=1, le=100)
    iterations: Optional[int] = Field(default=None, ge=100, le=10000)
    confidence_level: Optional[int] = Field(default=95, ge=50, le=99)


class SimulationCreate(SimulationBase):
    """Schema for creating a simulation"""
    parameters: Dict[str, Any] = Field(..., description="Simulation input parameters")
    assumptions: Optional[Dict[str, Any]] = Field(default=None, description="Assumptions for simulation")


class SimulationUpdate(BaseModel):
    """Schema for updating simulation"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    assumptions: Optional[Dict[str, Any]] = None
    time_horizon_years: Optional[int] = Field(None, ge=1, le=100)
    iterations: Optional[int] = Field(None, ge=100, le=10000)
    confidence_level: Optional[int] = Field(None, ge=50, le=99)
    is_favorite: Optional[bool] = None


class SimulationResponse(SimulationBase):
    """Schema for simulation response"""
    id: UUID
    user_id: UUID
    status: SimulationStatusEnum
    parameters: Dict[str, Any]
    assumptions: Optional[Dict[str, Any]] = None
    results: Optional[Dict[str, Any]] = None
    best_case: Optional[Dict[str, Any]] = None
    worst_case: Optional[Dict[str, Any]] = None
    base_case: Optional[Dict[str, Any]] = None
    recommendations: Optional[Dict[str, Any]] = None
    charts_data: Optional[Dict[str, Any]] = None
    is_favorite: bool
    executed_at: Optional[datetime] = None
    execution_time_ms: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    # Computed properties
    is_completed: Optional[bool] = None
    is_running: Optional[bool] = None
    is_draft: Optional[bool] = None
    has_results: Optional[bool] = None
    has_scenarios: Optional[bool] = None
    execution_time_seconds: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class SimulationListResponse(BaseModel):
    """Schema for paginated simulation list"""
    simulations: List[SimulationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SimulationSummary(BaseModel):
    """Schema for simulation statistics summary"""
    total_simulations: int
    draft_simulations: int
    completed_simulations: int
    failed_simulations: int
    favorite_simulations: int
    simulations_by_type: Dict[str, int]
    recent_simulations: List[SimulationResponse]
    average_execution_time_seconds: float


# Run simulation schemas
class RunSimulationRequest(BaseModel):
    """Schema for running a simulation"""
    run_scenarios: bool = Field(default=True, description="Run best/worst/base case scenarios")
    generate_recommendations: bool = Field(default=True, description="Generate AI recommendations")
    generate_charts: bool = Field(default=True, description="Generate chart data")


class RunSimulationResponse(BaseModel):
    """Schema for simulation run response"""
    id: UUID
    status: SimulationStatusEnum
    message: str
    task_id: Optional[str] = None  # Celery task ID
    estimated_time_seconds: Optional[int] = None


# Specific simulation parameter schemas
class RetirementSimulationParams(BaseModel):
    """Parameters for retirement simulation"""
    current_age: int = Field(..., ge=18, le=100)
    retirement_age: int = Field(..., ge=40, le=100)
    life_expectancy: int = Field(default=90, ge=60, le=120)
    current_savings: float = Field(..., ge=0)
    monthly_contribution: float = Field(..., ge=0)
    expected_return_rate: float = Field(default=7.0, ge=0, le=30)
    inflation_rate: float = Field(default=3.0, ge=0, le=20)
    desired_monthly_income: float = Field(..., ge=0)
    social_security_income: Optional[float] = Field(default=0, ge=0)
    pension_income: Optional[float] = Field(default=0, ge=0)


class InvestmentSimulationParams(BaseModel):
    """Parameters for investment simulation"""
    initial_investment: float = Field(..., ge=0)
    monthly_contribution: float = Field(default=0, ge=0)
    time_horizon_years: int = Field(..., ge=1, le=50)
    expected_return_rate: float = Field(..., ge=-50, le=100)
    volatility: float = Field(default=15.0, ge=0, le=100)
    expense_ratio: float = Field(default=0.5, ge=0, le=5)
    tax_rate: float = Field(default=20.0, ge=0, le=50)
    rebalance_frequency: str = Field(default="quarterly")


class LoanPayoffSimulationParams(BaseModel):
    """Parameters for loan payoff simulation"""
    loan_amount: float = Field(..., gt=0)
    interest_rate: float = Field(..., ge=0, le=50)
    loan_term_months: int = Field(..., ge=1, le=600)
    extra_payment: float = Field(default=0, ge=0)
    payment_frequency: str = Field(default="monthly")


class BudgetForecastParams(BaseModel):
    """Parameters for budget forecast simulation"""
    monthly_income: float = Field(..., gt=0)
    monthly_expenses: Dict[str, float] = Field(..., description="Category-wise expenses")
    savings_rate: float = Field(..., ge=0, le=100)
    income_growth_rate: float = Field(default=3.0, ge=-50, le=50)
    expense_growth_rate: float = Field(default=3.0, ge=-50, le=50)
    forecast_months: int = Field(default=12, ge=1, le=120)


class SavingsGoalParams(BaseModel):
    """Parameters for savings goal simulation"""
    goal_amount: float = Field(..., gt=0)
    current_savings: float = Field(default=0, ge=0)
    monthly_contribution: float = Field(..., ge=0)
    expected_return_rate: float = Field(default=5.0, ge=0, le=30)
    target_date: Optional[datetime] = None
    time_horizon_months: Optional[int] = Field(None, ge=1, le=600)


# Simulation results schemas
class SimulationResults(BaseModel):
    """Schema for simulation results"""
    simulation_id: UUID
    simulation_type: SimulationTypeEnum
    status: SimulationStatusEnum
    results: Dict[str, Any]
    best_case: Optional[Dict[str, Any]] = None
    worst_case: Optional[Dict[str, Any]] = None
    base_case: Optional[Dict[str, Any]] = None
    recommendations: Optional[Dict[str, Any]] = None
    charts_data: Optional[Dict[str, Any]] = None
    execution_time_seconds: float
    executed_at: datetime


class ScenarioComparison(BaseModel):
    """Schema for comparing simulation scenarios"""
    simulation_id: UUID
    scenarios: Dict[str, Dict[str, Any]]
    comparison_metrics: Dict[str, Any]
    recommendations: List[str]


# Filter schemas
class SimulationFilters(BaseModel):
    """Schema for filtering simulations"""
    simulation_type: Optional[SimulationTypeEnum] = None
    status: Optional[SimulationStatusEnum] = None
    is_favorite: Optional[bool] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None


# Made with Bob