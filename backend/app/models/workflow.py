"""
Autonomous workflow models for automated financial actions
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from app.db.base import Base


class WorkflowType(str, enum.Enum):
    """Workflow type enumeration"""
    BILL_PAYMENT = "bill_payment"
    SAVINGS_TRANSFER = "savings_transfer"
    INVESTMENT_REBALANCE = "investment_rebalance"
    DEBT_PAYMENT = "debt_payment"
    BUDGET_ALERT = "budget_alert"
    SPENDING_ALERT = "spending_alert"
    GOAL_TRACKING = "goal_tracking"
    TAX_REMINDER = "tax_reminder"
    SUBSCRIPTION_REVIEW = "subscription_review"
    CUSTOM = "custom"


class TriggerType(str, enum.Enum):
    """Workflow trigger type"""
    SCHEDULE = "schedule"  # Time-based (daily, weekly, monthly)
    BALANCE_THRESHOLD = "balance_threshold"  # Account balance condition
    SPENDING_THRESHOLD = "spending_threshold"  # Spending limit reached
    INCOME_RECEIVED = "income_received"  # Income detected
    BILL_DUE = "bill_due"  # Bill due date approaching
    GOAL_MILESTONE = "goal_milestone"  # Goal progress milestone
    MARKET_CONDITION = "market_condition"  # Market-based trigger
    MANUAL = "manual"  # User-initiated


class ActionType(str, enum.Enum):
    """Workflow action type"""
    TRANSFER_FUNDS = "transfer_funds"
    PAY_BILL = "pay_bill"
    SEND_NOTIFICATION = "send_notification"
    CREATE_RECOMMENDATION = "create_recommendation"
    UPDATE_BUDGET = "update_budget"
    REBALANCE_PORTFOLIO = "rebalance_portfolio"
    GENERATE_REPORT = "generate_report"
    CUSTOM_API_CALL = "custom_api_call"


class WorkflowStatus(str, enum.Enum):
    """Workflow status"""
    ACTIVE = "active"
    PAUSED = "paused"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class ExecutionStatus(str, enum.Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class AutonomousWorkflow(Base):
    """
    Autonomous workflow model for automated financial actions
    
    Attributes:
        id: Unique workflow identifier (UUID)
        user_id: Foreign key to user
        name: Workflow name
        description: Workflow description
        workflow_type: Type of workflow
        status: Workflow status (active/paused/inactive)
        trigger_type: Type of trigger
        trigger_config: Trigger configuration (schedule, conditions, etc.)
        action_type: Type of action to perform
        action_config: Action configuration (parameters, settings)
        conditions: Additional conditions to check before execution
        max_executions_per_day: Maximum executions allowed per day
        execution_count_today: Number of executions today
        total_executions: Total number of executions
        last_execution_at: Last execution timestamp
        last_execution_status: Status of last execution
        next_execution_at: Scheduled next execution time
        is_enabled: Whether workflow is enabled
        requires_approval: Whether execution requires user approval
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "autonomous_workflows"
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    workflow_type = Column(SQLEnum(WorkflowType), nullable=False, index=True)
    status = Column(SQLEnum(WorkflowStatus), nullable=False, default=WorkflowStatus.INACTIVE, index=True)
    
    # Trigger configuration
    trigger_type = Column(SQLEnum(TriggerType), nullable=False)
    trigger_config = Column(JSON, nullable=False)  # Schedule, conditions, thresholds
    
    # Action configuration
    action_type = Column(SQLEnum(ActionType), nullable=False)
    action_config = Column(JSON, nullable=False)  # Action parameters
    
    # Conditions and constraints
    conditions = Column(JSON, nullable=True)  # Additional conditions
    max_executions_per_day = Column(Integer, nullable=False, default=10)
    
    # Execution tracking
    execution_count_today = Column(Integer, nullable=False, default=0)
    total_executions = Column(Integer, nullable=False, default=0)
    last_execution_at = Column(DateTime, nullable=True)
    last_execution_status = Column(SQLEnum(ExecutionStatus), nullable=True)
    next_execution_at = Column(DateTime, nullable=True)
    
    # Settings
    is_enabled = Column(Boolean, default=True, nullable=False)
    requires_approval = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="workflows")
    executions = relationship("WorkflowExecution", back_populates="workflow", cascade="all, delete-orphan")
    
    @property
    def is_active(self) -> bool:
        """Check if workflow is active"""
        return self.status == WorkflowStatus.ACTIVE and self.is_enabled
    
    @property
    def is_paused(self) -> bool:
        """Check if workflow is paused"""
        return self.status == WorkflowStatus.PAUSED
    
    @property
    def can_execute_today(self) -> bool:
        """Check if workflow can execute today"""
        return self.execution_count_today < self.max_executions_per_day
    
    @property
    def last_execution_successful(self) -> bool:
        """Check if last execution was successful"""
        return self.last_execution_status == ExecutionStatus.COMPLETED
    
    @property
    def execution_success_rate(self) -> float:
        """Calculate execution success rate"""
        if self.total_executions == 0:
            return 0.0
        # This would need to be calculated from execution history
        return 0.0
    
    def activate(self):
        """Activate the workflow"""
        self.status = WorkflowStatus.ACTIVE
        self.is_enabled = True
        self.updated_at = datetime.utcnow()
    
    def pause(self):
        """Pause the workflow"""
        self.status = WorkflowStatus.PAUSED
        self.updated_at = datetime.utcnow()
    
    def deactivate(self):
        """Deactivate the workflow"""
        self.status = WorkflowStatus.INACTIVE
        self.is_enabled = False
        self.updated_at = datetime.utcnow()
    
    def archive(self):
        """Archive the workflow"""
        self.status = WorkflowStatus.ARCHIVED
        self.is_enabled = False
        self.updated_at = datetime.utcnow()
    
    def record_execution(self, status: ExecutionStatus):
        """Record a workflow execution"""
        self.last_execution_at = datetime.utcnow()
        self.last_execution_status = status
        self.total_executions += 1
        self.execution_count_today += 1
        self.updated_at = datetime.utcnow()
    
    def reset_daily_count(self):
        """Reset daily execution count"""
        self.execution_count_today = 0
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f"<AutonomousWorkflow(id={self.id}, name={self.name}, type={self.workflow_type}, status={self.status})>"


class WorkflowExecution(Base):
    """
    Workflow execution history model
    
    Attributes:
        id: Unique execution identifier (UUID)
        workflow_id: Foreign key to workflow
        status: Execution status
        trigger_data: Data that triggered the execution
        action_data: Data used for action execution
        result: Execution result
        error_message: Error message if failed
        execution_time_ms: Execution time in milliseconds
        started_at: Execution start time
        completed_at: Execution completion time
        created_at: Record creation timestamp
    """
    
    __tablename__ = "workflow_executions"
    
    # Foreign keys
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("autonomous_workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Execution details
    status = Column(SQLEnum(ExecutionStatus), nullable=False, default=ExecutionStatus.PENDING, index=True)
    trigger_data = Column(JSON, nullable=True)  # Data that triggered execution
    action_data = Column(JSON, nullable=True)  # Data used for action
    result = Column(JSON, nullable=True)  # Execution result
    error_message = Column(Text, nullable=True)
    
    # Timing
    execution_time_ms = Column(Integer, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    workflow = relationship("AutonomousWorkflow", back_populates="executions")
    
    @property
    def is_completed(self) -> bool:
        """Check if execution is completed"""
        return self.status == ExecutionStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if execution failed"""
        return self.status == ExecutionStatus.FAILED
    
    @property
    def is_running(self) -> bool:
        """Check if execution is running"""
        return self.status == ExecutionStatus.RUNNING
    
    @property
    def execution_time_seconds(self) -> float:
        """Get execution time in seconds"""
        if self.execution_time_ms:
            return round(self.execution_time_ms / 1000, 2)
        return 0.0
    
    def mark_as_running(self):
        """Mark execution as running"""
        self.status = ExecutionStatus.RUNNING
        self.started_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def mark_as_completed(self, result: dict = None, execution_time_ms: int = None):
        """Mark execution as completed"""
        self.status = ExecutionStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        if result:
            self.result = result
        if execution_time_ms:
            self.execution_time_ms = execution_time_ms
    
    def mark_as_failed(self, error_message: str):
        """Mark execution as failed"""
        self.status = ExecutionStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.error_message = error_message
    
    def mark_as_skipped(self, reason: str = None):
        """Mark execution as skipped"""
        self.status = ExecutionStatus.SKIPPED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        if reason:
            self.error_message = reason
    
    def __repr__(self):
        return f"<WorkflowExecution(id={self.id}, workflow_id={self.workflow_id}, status={self.status})>"


# Made with Bob