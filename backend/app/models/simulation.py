"""
Financial simulation models for scenario planning and forecasting
"""
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from app.db.base import Base


class SimulationType(str, enum.Enum):
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


class SimulationStatus(str, enum.Enum):
    """Simulation execution status"""
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class FinancialSimulation(Base):
    """
    Financial simulation model for scenario planning
    
    Attributes:
        id: Unique simulation identifier (UUID)
        user_id: Foreign key to user
        name: Simulation name
        description: Simulation description
        simulation_type: Type of simulation
        status: Execution status
        parameters: Input parameters for simulation
        results: Simulation results and projections
        assumptions: Assumptions used in simulation
        time_horizon_years: Simulation time horizon
        iterations: Number of Monte Carlo iterations (if applicable)
        confidence_level: Confidence level for projections (0-100)
        best_case: Best case scenario results
        worst_case: Worst case scenario results
        base_case: Base case scenario results
        recommendations: AI-generated recommendations based on results
        charts_data: Data for visualization charts
        is_favorite: Whether user marked as favorite
        executed_at: When simulation was executed
        execution_time_ms: Execution time in milliseconds
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "financial_simulations"
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    simulation_type = Column(SQLEnum(SimulationType), nullable=False, index=True)
    status = Column(SQLEnum(SimulationStatus), nullable=False, default=SimulationStatus.DRAFT, index=True)
    
    # Simulation configuration
    parameters = Column(JSON, nullable=False)  # Input parameters
    assumptions = Column(JSON, nullable=True)  # Assumptions (inflation, returns, etc.)
    time_horizon_years = Column(Integer, nullable=False, default=30)
    iterations = Column(Integer, nullable=True)  # For Monte Carlo simulations
    confidence_level = Column(Integer, nullable=True, default=95)  # 0-100
    
    # Results
    results = Column(JSON, nullable=True)  # Main results
    best_case = Column(JSON, nullable=True)  # Best case scenario
    worst_case = Column(JSON, nullable=True)  # Worst case scenario
    base_case = Column(JSON, nullable=True)  # Base case scenario
    recommendations = Column(JSON, nullable=True)  # AI recommendations
    charts_data = Column(JSON, nullable=True)  # Data for charts
    
    # Metadata
    is_favorite = Column(Boolean, default=False, nullable=False)
    executed_at = Column(DateTime, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="simulations")
    
    @property
    def is_completed(self) -> bool:
        """Check if simulation is completed"""
        return self.status == SimulationStatus.COMPLETED
    
    @property
    def is_running(self) -> bool:
        """Check if simulation is running"""
        return self.status == SimulationStatus.RUNNING
    
    @property
    def is_draft(self) -> bool:
        """Check if simulation is in draft"""
        return self.status == SimulationStatus.DRAFT
    
    @property
    def has_results(self) -> bool:
        """Check if simulation has results"""
        return self.results is not None
    
    @property
    def has_scenarios(self) -> bool:
        """Check if simulation has scenario analysis"""
        return self.best_case is not None and self.worst_case is not None
    
    @property
    def execution_time_seconds(self) -> float:
        """Get execution time in seconds"""
        if self.execution_time_ms:
            return round(self.execution_time_ms / 1000, 2)
        return 0.0
    
    def mark_as_running(self):
        """Mark simulation as running"""
        self.status = SimulationStatus.RUNNING
        self.updated_at = datetime.utcnow()
    
    def mark_as_completed(self, results: dict, execution_time_ms: int = None,
                         best_case: dict = None, worst_case: dict = None, 
                         base_case: dict = None, recommendations: dict = None):
        """Mark simulation as completed with results"""
        self.status = SimulationStatus.COMPLETED
        self.executed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.results = results
        
        if execution_time_ms:
            self.execution_time_ms = execution_time_ms
        if best_case:
            self.best_case = best_case
        if worst_case:
            self.worst_case = worst_case
        if base_case:
            self.base_case = base_case
        if recommendations:
            self.recommendations = recommendations
    
    def mark_as_failed(self, error_message: str = None):
        """Mark simulation as failed"""
        self.status = SimulationStatus.FAILED
        self.updated_at = datetime.utcnow()
        
        if error_message:
            if self.results is None:
                self.results = {}
            self.results["error"] = error_message
    
    def archive(self):
        """Archive the simulation"""
        self.status = SimulationStatus.ARCHIVED
        self.updated_at = datetime.utcnow()
    
    def toggle_favorite(self):
        """Toggle favorite status"""
        self.is_favorite = not self.is_favorite
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f"<FinancialSimulation(id={self.id}, name={self.name}, type={self.simulation_type}, status={self.status})>"


# Made with Bob