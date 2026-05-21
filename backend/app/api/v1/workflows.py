"""
Workflows API endpoints
Handles autonomous workflow management and execution
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.workflow import WorkflowType, WorkflowStatus, TriggerType, ActionType, ExecutionStatus
from app.schemas.workflow import (
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowResponse,
    WorkflowSummary,
    WorkflowExecutionResponse,
    ActivateWorkflowResponse,
    PauseWorkflowResponse,
    ExecuteWorkflowRequest,
    ExecuteWorkflowResponse,
)
from app.services.workflow_service import workflow_service


router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.post("/", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    workflow_data: WorkflowCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new autonomous workflow
    
    - **name**: Workflow name
    - **workflow_type**: Type of workflow (bill_payment, savings_transfer, etc.)
    - **trigger_type**: Type of trigger (schedule, balance_threshold, etc.)
    - **action_type**: Type of action (transfer_funds, send_notification, etc.)
    - **trigger_config**: Trigger configuration (schedule, conditions, etc.)
    - **action_config**: Action configuration (parameters, settings)
    """
    try:
        workflow = await workflow_service.create_workflow(
            db=db,
            user_id=current_user.id,
            workflow_data=workflow_data,
        )
        return workflow
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workflow: {str(e)}"
        )


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific workflow by ID"""
    workflow = await workflow_service.get_workflow(db, workflow_id, current_user.id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    return workflow


@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(
    workflow_type: Optional[WorkflowType] = Query(None),
    status_filter: Optional[WorkflowStatus] = Query(None, alias="status"),
    trigger_type: Optional[TriggerType] = Query(None),
    action_type: Optional[ActionType] = Query(None),
    is_enabled: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List user's workflows with optional filters
    
    - **workflow_type**: Filter by workflow type
    - **status**: Filter by workflow status
    - **trigger_type**: Filter by trigger type
    - **action_type**: Filter by action type
    - **is_enabled**: Filter by enabled status
    - **skip**: Number of workflows to skip
    - **limit**: Maximum number of workflows to return
    """
    workflows = await workflow_service.list_workflows(
        db=db,
        user_id=current_user.id,
        workflow_type=workflow_type,
        status=status_filter,
        trigger_type=trigger_type,
        action_type=action_type,
        is_enabled=is_enabled,
        skip=skip,
        limit=limit,
    )
    return workflows


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: UUID,
    update_data: WorkflowUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update workflow configuration"""
    workflow = await workflow_service.update_workflow(
        db=db,
        workflow_id=workflow_id,
        user_id=current_user.id,
        update_data=update_data,
    )
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    return workflow


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a workflow"""
    success = await workflow_service.delete_workflow(
        db=db,
        workflow_id=workflow_id,
        user_id=current_user.id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    return None


@router.post("/{workflow_id}/activate", response_model=ActivateWorkflowResponse)
async def activate_workflow(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Activate a workflow
    
    Sets the workflow status to ACTIVE and enables automatic execution
    based on the configured triggers.
    """
    workflow = await workflow_service.activate_workflow(
        db=db,
        workflow_id=workflow_id,
        user_id=current_user.id,
    )
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    return ActivateWorkflowResponse(
        id=str(workflow.id),
        status=workflow.status,
        message="Workflow activated successfully",
        next_execution_at=workflow.next_execution_at,
    )


@router.post("/{workflow_id}/pause", response_model=PauseWorkflowResponse)
async def pause_workflow(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Pause a workflow
    
    Temporarily stops workflow execution without deactivating it.
    Can be resumed by activating again.
    """
    workflow = await workflow_service.pause_workflow(
        db=db,
        workflow_id=workflow_id,
        user_id=current_user.id,
    )
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    return PauseWorkflowResponse(
        id=str(workflow.id),
        status=workflow.status,
        message="Workflow paused successfully",
    )


@router.post("/{workflow_id}/deactivate", response_model=PauseWorkflowResponse)
async def deactivate_workflow(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Deactivate a workflow
    
    Stops workflow execution and sets status to INACTIVE.
    """
    workflow = await workflow_service.deactivate_workflow(
        db=db,
        workflow_id=workflow_id,
        user_id=current_user.id,
    )
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    return PauseWorkflowResponse(
        id=str(workflow.id),
        status=workflow.status,
        message="Workflow deactivated successfully",
    )


@router.post("/{workflow_id}/execute", response_model=ExecuteWorkflowResponse)
async def execute_workflow(
    workflow_id: UUID,
    execution_request: ExecuteWorkflowRequest = ExecuteWorkflowRequest(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute a workflow manually
    
    Triggers immediate workflow execution. Can override conditions and run in test mode.
    
    - **override_conditions**: Execute even if conditions are not met
    - **test_mode**: Run in test mode without actual execution
    """
    try:
        execution = await workflow_service.execute_workflow(
            db=db,
            workflow_id=workflow_id,
            user_id=current_user.id,
            execution_request=execution_request,
        )
        
        return ExecuteWorkflowResponse(
            workflow_id=str(workflow_id),
            execution_id=str(execution.id),
            status=execution.status,
            message="Workflow executed successfully" if execution.is_completed else "Workflow execution started",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow execution failed: {str(e)}"
        )


@router.get("/{workflow_id}/executions", response_model=List[WorkflowExecutionResponse])
async def get_workflow_executions(
    workflow_id: UUID,
    status_filter: Optional[ExecutionStatus] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get execution history for a workflow
    
    - **status**: Filter by execution status
    - **skip**: Number of executions to skip
    - **limit**: Maximum number of executions to return
    """
    executions = await workflow_service.get_workflow_executions(
        db=db,
        workflow_id=workflow_id,
        user_id=current_user.id,
        status=status_filter,
        skip=skip,
        limit=limit,
    )
    return executions


@router.get("/summary/stats", response_model=WorkflowSummary)
async def get_workflow_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get workflow statistics summary
    
    Returns:
    - Total workflows by status
    - Execution counts
    - Workflows by type
    - Recent workflows
    - Success rate
    """
    summary = await workflow_service.get_workflow_summary(
        db=db,
        user_id=current_user.id,
    )
    return summary


# Convenience endpoints for common workflow types

@router.post("/quick/bill-payment", response_model=WorkflowResponse)
async def create_bill_payment_workflow(
    name: str = Query(..., description="Workflow name"),
    bill_amount: float = Query(..., gt=0),
    from_account_id: str = Query(...),
    to_account_id: str = Query(...),
    days_before_due: int = Query(3, ge=0, le=30),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Quick create a bill payment workflow
    
    Automatically pays bills when they're due
    """
    workflow_data = WorkflowCreate(
        name=name,
        description=f"Automatic bill payment of ${bill_amount}",
        workflow_type=WorkflowType.BILL_PAYMENT,
        trigger_type=TriggerType.BILL_DUE,
        action_type=ActionType.PAY_BILL,
        trigger_config={
            "days_before_due": days_before_due,
        },
        action_config={
            "from_account_id": from_account_id,
            "to_account_id": to_account_id,
            "amount": bill_amount,
        },
        requires_approval=True,
    )
    
    workflow = await workflow_service.create_workflow(db, current_user.id, workflow_data)
    return workflow


@router.post("/quick/savings-transfer", response_model=WorkflowResponse)
async def create_savings_transfer_workflow(
    name: str = Query(..., description="Workflow name"),
    from_account_id: str = Query(...),
    to_account_id: str = Query(...),
    transfer_percentage: float = Query(..., gt=0, le=100),
    frequency: str = Query("monthly", regex="^(daily|weekly|monthly)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Quick create a savings transfer workflow
    
    Automatically transfers a percentage of income to savings
    """
    workflow_data = WorkflowCreate(
        name=name,
        description=f"Automatic savings transfer of {transfer_percentage}%",
        workflow_type=WorkflowType.SAVINGS_TRANSFER,
        trigger_type=TriggerType.INCOME_RECEIVED,
        action_type=ActionType.TRANSFER_FUNDS,
        trigger_config={
            "frequency": frequency,
        },
        action_config={
            "from_account_id": from_account_id,
            "to_account_id": to_account_id,
            "percentage": transfer_percentage,
        },
        requires_approval=False,
    )
    
    workflow = await workflow_service.create_workflow(db, current_user.id, workflow_data)
    return workflow


@router.post("/quick/spending-alert", response_model=WorkflowResponse)
async def create_spending_alert_workflow(
    name: str = Query(..., description="Workflow name"),
    category: str = Query(...),
    threshold_amount: float = Query(..., gt=0),
    notification_type: str = Query("email", regex="^(email|sms|push)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Quick create a spending alert workflow
    
    Sends notification when spending in a category exceeds threshold
    """
    workflow_data = WorkflowCreate(
        name=name,
        description=f"Alert when {category} spending exceeds ${threshold_amount}",
        workflow_type=WorkflowType.SPENDING_ALERT,
        trigger_type=TriggerType.SPENDING_THRESHOLD,
        action_type=ActionType.SEND_NOTIFICATION,
        trigger_config={
            "category": category,
            "threshold_amount": threshold_amount,
            "comparison": "greater_than",
        },
        action_config={
            "notification_type": notification_type,
            "subject": f"Spending Alert: {category}",
            "message": f"Your {category} spending has exceeded ${threshold_amount}",
            "priority": "high",
        },
        requires_approval=False,
    )
    
    workflow = await workflow_service.create_workflow(db, current_user.id, workflow_data)
    return workflow


# Made with Bob