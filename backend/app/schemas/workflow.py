"""
Pydantic schemas for autonomous workflows and automation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import UUID


class WorkflowTypeEnum(str, Enum):
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


class TriggerTypeEnum(str, Enum):
    """Workflow trigger type"""
    SCHEDULE = "schedule"
    BALANCE_THRESHOLD = "balance_threshold"
    SPENDING_THRESHOLD = "spending_threshold"
    INCOME_RECEIVED = "income_received"
    BILL_DUE = "bill_due"
    GOAL_MILESTONE = "goal_milestone"
    MARKET_CONDITION = "market_condition"
    MANUAL = "manual"


class ActionTypeEnum(str, Enum):
    """Workflow action type"""
    TRANSFER_FUNDS = "transfer_funds"
    PAY_BILL = "pay_bill"
    SEND_NOTIFICATION = "send_notification"
    CREATE_RECOMMENDATION = "create_recommendation"
    UPDATE_BUDGET = "update_budget"
    REBALANCE_PORTFOLIO = "rebalance_portfolio"
    GENERATE_REPORT = "generate_report"
    CUSTOM_API_CALL = "custom_api_call"


class WorkflowStatusEnum(str, Enum):
    """Workflow status"""
    ACTIVE = "active"
    PAUSED = "paused"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class ExecutionStatusEnum(str, Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


# Base schemas
class WorkflowBase(BaseModel):
    """Base workflow schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    workflow_type: WorkflowTypeEnum
    trigger_type: TriggerTypeEnum
    action_type: ActionTypeEnum
    max_executions_per_day: int = Field(default=10, ge=1, le=100)
    requires_approval: bool = Field(default=False)


class WorkflowCreate(WorkflowBase):
    """Schema for creating a workflow"""
    trigger_config: Dict[str, Any] = Field(..., description="Trigger configuration")
    action_config: Dict[str, Any] = Field(..., description="Action configuration")
    conditions: Optional[Dict[str, Any]] = Field(default=None, description="Additional conditions")


class WorkflowUpdate(BaseModel):
    """Schema for updating workflow"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    trigger_config: Optional[Dict[str, Any]] = None
    action_config: Optional[Dict[str, Any]] = None
    conditions: Optional[Dict[str, Any]] = None
    max_executions_per_day: Optional[int] = Field(None, ge=1, le=100)
    requires_approval: Optional[bool] = None
    is_enabled: Optional[bool] = None


class WorkflowResponse(WorkflowBase):
    """Schema for workflow response"""
    id: UUID
    user_id: UUID
    status: WorkflowStatusEnum
    trigger_config: Dict[str, Any]
    action_config: Dict[str, Any]
    conditions: Optional[Dict[str, Any]] = None
    execution_count_today: int
    total_executions: int
    last_execution_at: Optional[datetime] = None
    last_execution_status: Optional[ExecutionStatusEnum] = None
    next_execution_at: Optional[datetime] = None
    is_enabled: bool
    created_at: datetime
    updated_at: datetime
    
    # Computed properties
    is_active: Optional[bool] = None
    is_paused: Optional[bool] = None
    can_execute_today: Optional[bool] = None
    last_execution_successful: Optional[bool] = None

    class Config:
        from_attributes = True


class WorkflowListResponse(BaseModel):
    """Schema for paginated workflow list"""
    workflows: List[WorkflowResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class WorkflowSummary(BaseModel):
    """Schema for workflow statistics summary"""
    total_workflows: int
    active_workflows: int
    paused_workflows: int
    inactive_workflows: int
    total_executions_today: int
    total_executions_all_time: int
    workflows_by_type: Dict[str, int]
    recent_workflows: List[WorkflowResponse]
    success_rate: float


# Workflow execution schemas
class WorkflowExecutionResponse(BaseModel):
    """Schema for workflow execution response"""
    id: UUID
    workflow_id: UUID
    status: ExecutionStatusEnum
    trigger_data: Optional[Dict[str, Any]] = None
    action_data: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Computed properties
    is_completed: Optional[bool] = None
    is_failed: Optional[bool] = None
    is_running: Optional[bool] = None
    execution_time_seconds: Optional[float] = None

    class Config:
        from_attributes = True


class WorkflowExecutionListResponse(BaseModel):
    """Schema for paginated execution list"""
    executions: List[WorkflowExecutionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# Workflow action schemas
class ActivateWorkflowRequest(BaseModel):
    """Schema for activating a workflow"""
    schedule_next_execution: bool = Field(default=True)


class ActivateWorkflowResponse(BaseModel):
    """Schema for workflow activation response"""
    id: str
    status: WorkflowStatusEnum
    message: str
    next_execution_at: Optional[datetime] = None


class PauseWorkflowResponse(BaseModel):
    """Schema for workflow pause response"""
    id: str
    status: WorkflowStatusEnum
    message: str


class ExecuteWorkflowRequest(BaseModel):
    """Schema for manual workflow execution"""
    override_conditions: bool = Field(default=False, description="Execute even if conditions not met")
    test_mode: bool = Field(default=False, description="Run in test mode without actual execution")


class ExecuteWorkflowResponse(BaseModel):
    """Schema for workflow execution response"""
    workflow_id: str
    execution_id: str
    status: ExecutionStatusEnum
    message: str
    task_id: Optional[str] = None  # Celery task ID


# Trigger configuration schemas
class ScheduleTriggerConfig(BaseModel):
    """Configuration for schedule-based triggers"""
    frequency: str = Field(..., description="daily, weekly, monthly, custom")
    time: str = Field(..., description="Time in HH:MM format")
    days_of_week: Optional[List[int]] = Field(default=None, description="0=Monday, 6=Sunday")
    day_of_month: Optional[int] = Field(default=None, ge=1, le=31)
    timezone: str = Field(default="UTC")


class ThresholdTriggerConfig(BaseModel):
    """Configuration for threshold-based triggers"""
    account_id: Optional[str] = None
    threshold_amount: float = Field(...)
    comparison: str = Field(..., description="greater_than, less_than, equals")
    category: Optional[str] = None


class BillDueTriggerConfig(BaseModel):
    """Configuration for bill due triggers"""
    days_before_due: int = Field(default=3, ge=0, le=30)
    bill_categories: Optional[List[str]] = None


# Action configuration schemas
class TransferFundsActionConfig(BaseModel):
    """Configuration for fund transfer actions"""
    from_account_id: str
    to_account_id: str
    amount: Optional[float] = None
    percentage: Optional[float] = Field(None, ge=0, le=100)
    description: Optional[str] = None


class NotificationActionConfig(BaseModel):
    """Configuration for notification actions"""
    notification_type: str = Field(..., description="email, sms, push")
    subject: str
    message: str
    priority: str = Field(default="normal", description="low, normal, high, urgent")


class RecommendationActionConfig(BaseModel):
    """Configuration for creating recommendations"""
    recommendation_type: str
    priority: str = Field(default="medium")
    auto_generate_content: bool = Field(default=True)


# Filter schemas
class WorkflowFilters(BaseModel):
    """Schema for filtering workflows"""
    workflow_type: Optional[WorkflowTypeEnum] = None
    status: Optional[WorkflowStatusEnum] = None
    trigger_type: Optional[TriggerTypeEnum] = None
    action_type: Optional[ActionTypeEnum] = None
    is_enabled: Optional[bool] = None


class ExecutionFilters(BaseModel):
    """Schema for filtering workflow executions"""
    workflow_id: Optional[str] = None
    status: Optional[ExecutionStatusEnum] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None


# Workflow analytics
class WorkflowAnalytics(BaseModel):
    """Schema for workflow analytics"""
    workflow_id: str
    total_executions: int
    successful_executions: int
    failed_executions: int
    skipped_executions: int
    success_rate: float
    average_execution_time_ms: float
    last_7_days_executions: List[Dict[str, Any]]
    execution_trend: str  # increasing, decreasing, stable


# Made with Bob