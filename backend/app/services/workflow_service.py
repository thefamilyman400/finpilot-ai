"""
Workflow Service
Handles autonomous workflow management, execution, and scheduling
"""
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.workflow import (
    AutonomousWorkflow,
    WorkflowExecution,
    WorkflowType,
    WorkflowStatus,
    TriggerType,
    ActionType,
    ExecutionStatus,
)
from app.schemas.workflow import (
    WorkflowCreate,
    WorkflowUpdate,
    ExecuteWorkflowRequest,
)


class WorkflowService:
    """Service for autonomous workflow management"""
    
    async def create_workflow(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        workflow_data: WorkflowCreate,
    ) -> AutonomousWorkflow:
        """
        Create a new autonomous workflow
        
        Args:
            db: Database session
            user_id: User ID
            workflow_data: Workflow creation data
            
        Returns:
            Created workflow
        """
        workflow = AutonomousWorkflow(
            user_id=user_id,
            name=workflow_data.name,
            description=workflow_data.description,
            workflow_type=workflow_data.workflow_type,
            trigger_type=workflow_data.trigger_type,
            trigger_config=workflow_data.trigger_config,
            action_type=workflow_data.action_type,
            action_config=workflow_data.action_config,
            conditions=workflow_data.conditions,
            max_executions_per_day=workflow_data.max_executions_per_day,
            requires_approval=workflow_data.requires_approval,
            status=WorkflowStatus.INACTIVE,
            is_enabled=False,
        )
        
        db.add(workflow)
        await db.commit()
        await db.refresh(workflow)
        
        return workflow
    
    async def get_workflow(
        self,
        db: AsyncSession,
        workflow_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Optional[AutonomousWorkflow]:
        """Get a workflow by ID"""
        result = await db.execute(
            select(AutonomousWorkflow).where(
                and_(
                    AutonomousWorkflow.id == workflow_id,
                    AutonomousWorkflow.user_id == user_id,
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def list_workflows(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        workflow_type: Optional[WorkflowType] = None,
        status: Optional[WorkflowStatus] = None,
        trigger_type: Optional[TriggerType] = None,
        action_type: Optional[ActionType] = None,
        is_enabled: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[AutonomousWorkflow]:
        """List user's workflows with optional filters"""
        query = select(AutonomousWorkflow).where(AutonomousWorkflow.user_id == user_id)
        
        if workflow_type:
            query = query.where(AutonomousWorkflow.workflow_type == workflow_type)
        
        if status:
            query = query.where(AutonomousWorkflow.status == status)
        
        if trigger_type:
            query = query.where(AutonomousWorkflow.trigger_type == trigger_type)
        
        if action_type:
            query = query.where(AutonomousWorkflow.action_type == action_type)
        
        if is_enabled is not None:
            query = query.where(AutonomousWorkflow.is_enabled == is_enabled)
        
        query = query.order_by(AutonomousWorkflow.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def update_workflow(
        self,
        db: AsyncSession,
        workflow_id: uuid.UUID,
        user_id: uuid.UUID,
        update_data: WorkflowUpdate,
    ) -> Optional[AutonomousWorkflow]:
        """Update workflow configuration"""
        workflow = await self.get_workflow(db, workflow_id, user_id)
        if not workflow:
            return None
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(workflow, field, value)
        
        workflow.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(workflow)
        return workflow
    
    async def delete_workflow(
        self,
        db: AsyncSession,
        workflow_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """Delete a workflow"""
        workflow = await self.get_workflow(db, workflow_id, user_id)
        if not workflow:
            return False
        
        await db.delete(workflow)
        await db.commit()
        return True
    
    async def activate_workflow(
        self,
        db: AsyncSession,
        workflow_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Optional[AutonomousWorkflow]:
        """Activate a workflow"""
        workflow = await self.get_workflow(db, workflow_id, user_id)
        if not workflow:
            return None
        
        workflow.activate()
        
        # Schedule next execution based on trigger type
        if workflow.trigger_type == TriggerType.SCHEDULE:
            workflow.next_execution_at = self._calculate_next_execution(workflow.trigger_config)
        
        await db.commit()
        await db.refresh(workflow)
        return workflow
    
    async def pause_workflow(
        self,
        db: AsyncSession,
        workflow_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Optional[AutonomousWorkflow]:
        """Pause a workflow"""
        workflow = await self.get_workflow(db, workflow_id, user_id)
        if not workflow:
            return None
        
        workflow.pause()
        
        await db.commit()
        await db.refresh(workflow)
        return workflow
    
    async def deactivate_workflow(
        self,
        db: AsyncSession,
        workflow_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Optional[AutonomousWorkflow]:
        """Deactivate a workflow"""
        workflow = await self.get_workflow(db, workflow_id, user_id)
        if not workflow:
            return None
        
        workflow.deactivate()
        
        await db.commit()
        await db.refresh(workflow)
        return workflow
    
    async def execute_workflow(
        self,
        db: AsyncSession,
        workflow_id: uuid.UUID,
        user_id: uuid.UUID,
        execution_request: Optional[ExecuteWorkflowRequest] = None,
    ) -> WorkflowExecution:
        """
        Execute a workflow manually or automatically
        
        Args:
            db: Database session
            workflow_id: Workflow ID
            user_id: User ID
            execution_request: Optional execution parameters
            
        Returns:
            Workflow execution record
        """
        workflow = await self.get_workflow(db, workflow_id, user_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Check if workflow can execute
        if not execution_request or not execution_request.override_conditions:
            if not workflow.is_active:
                raise HTTPException(status_code=400, detail="Workflow is not active")
            
            if not workflow.can_execute_today:
                raise HTTPException(
                    status_code=400,
                    detail=f"Daily execution limit reached ({workflow.max_executions_per_day})"
                )
        
        # Create execution record
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            status=ExecutionStatus.PENDING,
            trigger_data={"manual": True, "user_id": str(user_id)},
        )
        
        db.add(execution)
        await db.commit()
        await db.refresh(execution)
        
        # Mark as running
        execution.mark_as_running()
        await db.commit()
        
        try:
            # Execute workflow action
            start_time = datetime.utcnow()
            
            # TODO: Implement actual workflow execution logic based on action_type
            # For now, simulate execution
            test_mode = execution_request.test_mode if execution_request else False
            
            result = await self._execute_workflow_action(
                workflow=workflow,
                execution=execution,
                test_mode=test_mode,
            )
            
            # Calculate execution time
            execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Mark as completed
            execution.mark_as_completed(result=result, execution_time_ms=execution_time_ms)
            workflow.record_execution(ExecutionStatus.COMPLETED)
            
            await db.commit()
            await db.refresh(execution)
            
            return execution
            
        except Exception as e:
            # Mark as failed
            execution.mark_as_failed(str(e))
            workflow.record_execution(ExecutionStatus.FAILED)
            
            await db.commit()
            await db.refresh(execution)
            
            raise HTTPException(
                status_code=500,
                detail=f"Workflow execution failed: {str(e)}"
            )
    
    async def get_workflow_executions(
        self,
        db: AsyncSession,
        workflow_id: uuid.UUID,
        user_id: uuid.UUID,
        status: Optional[ExecutionStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[WorkflowExecution]:
        """Get execution history for a workflow"""
        # Verify workflow ownership
        workflow = await self.get_workflow(db, workflow_id, user_id)
        if not workflow:
            return []
        
        query = select(WorkflowExecution).where(WorkflowExecution.workflow_id == workflow_id)
        
        if status:
            query = query.where(WorkflowExecution.status == status)
        
        query = query.order_by(WorkflowExecution.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_workflow_summary(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """Get workflow statistics summary for user"""
        # Count workflows by status
        status_counts = await db.execute(
            select(
                AutonomousWorkflow.status,
                func.count(AutonomousWorkflow.id)
            )
            .where(AutonomousWorkflow.user_id == user_id)
            .group_by(AutonomousWorkflow.status)
        )
        
        status_dict = {status: count for status, count in status_counts}
        
        # Count workflows by type
        type_counts = await db.execute(
            select(
                AutonomousWorkflow.workflow_type,
                func.count(AutonomousWorkflow.id)
            )
            .where(AutonomousWorkflow.user_id == user_id)
            .group_by(AutonomousWorkflow.workflow_type)
        )
        
        type_dict = {wf_type.value: count for wf_type, count in type_counts}
        
        # Get total executions
        total_executions = await db.execute(
            select(func.sum(AutonomousWorkflow.total_executions))
            .where(AutonomousWorkflow.user_id == user_id)
        )
        total_exec_count = total_executions.scalar() or 0
        
        # Get today's executions
        today_executions = await db.execute(
            select(func.sum(AutonomousWorkflow.execution_count_today))
            .where(AutonomousWorkflow.user_id == user_id)
        )
        today_exec_count = today_executions.scalar() or 0
        
        # Get recent workflows
        recent_workflows = await self.list_workflows(
            db=db,
            user_id=user_id,
            skip=0,
            limit=5,
        )
        
        return {
            "total_workflows": sum(status_dict.values()),
            "active_workflows": status_dict.get(WorkflowStatus.ACTIVE, 0),
            "paused_workflows": status_dict.get(WorkflowStatus.PAUSED, 0),
            "inactive_workflows": status_dict.get(WorkflowStatus.INACTIVE, 0),
            "total_executions_today": today_exec_count,
            "total_executions_all_time": total_exec_count,
            "workflows_by_type": type_dict,
            "recent_workflows": recent_workflows,
            "success_rate": 0.0,  # TODO: Calculate from execution history
        }
    
    def _calculate_next_execution(self, trigger_config: Dict[str, Any]) -> datetime:
        """
        Calculate next execution time based on schedule configuration
        
        Args:
            trigger_config: Trigger configuration with schedule details
            
        Returns:
            Next execution datetime
        """
        # TODO: Implement proper schedule calculation
        # For now, default to 1 day from now
        frequency = trigger_config.get("frequency", "daily")
        
        if frequency == "daily":
            return datetime.utcnow() + timedelta(days=1)
        elif frequency == "weekly":
            return datetime.utcnow() + timedelta(weeks=1)
        elif frequency == "monthly":
            return datetime.utcnow() + timedelta(days=30)
        else:
            return datetime.utcnow() + timedelta(days=1)
    
    async def _execute_workflow_action(
        self,
        workflow: AutonomousWorkflow,
        execution: WorkflowExecution,
        test_mode: bool = False,
    ) -> Dict[str, Any]:
        """
        Execute the workflow action
        
        Args:
            workflow: Workflow to execute
            execution: Execution record
            test_mode: Whether to run in test mode
            
        Returns:
            Execution result
        """
        # TODO: Implement actual action execution based on action_type
        # This is a placeholder implementation
        
        action_type = workflow.action_type
        action_config = workflow.action_config
        
        result = {
            "action_type": action_type.value,
            "test_mode": test_mode,
            "executed_at": datetime.utcnow().isoformat(),
            "message": f"Workflow action '{action_type.value}' executed successfully",
        }
        
        if action_type == ActionType.TRANSFER_FUNDS:
            result["details"] = {
                "from_account": action_config.get("from_account_id"),
                "to_account": action_config.get("to_account_id"),
                "amount": action_config.get("amount"),
                "status": "simulated" if test_mode else "completed",
            }
        
        elif action_type == ActionType.SEND_NOTIFICATION:
            result["details"] = {
                "notification_type": action_config.get("notification_type"),
                "subject": action_config.get("subject"),
                "status": "sent" if not test_mode else "simulated",
            }
        
        elif action_type == ActionType.CREATE_RECOMMENDATION:
            result["details"] = {
                "recommendation_type": action_config.get("recommendation_type"),
                "priority": action_config.get("priority"),
                "status": "created" if not test_mode else "simulated",
            }
        
        else:
            result["details"] = {
                "message": f"Action type '{action_type.value}' execution not yet implemented",
                "status": "placeholder",
            }
        
        return result


# Singleton instance
workflow_service = WorkflowService()

# Made with Bob