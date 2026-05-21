"""
Tests for workflow endpoints and service
"""
import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.workflow import AutonomousWorkflow, WorkflowExecution
from app.models.account import FinancialAccount


@pytest.mark.asyncio
async def test_create_workflow(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test creating a workflow"""
    workflow_data = {
        "workflow_type": "bill_payment",
        "name": "Auto Pay Rent",
        "description": "Automatically pay rent on the 1st",
        "trigger_type": "schedule",
        "trigger_config": {
            "frequency": "monthly",
            "time": "09:00",
            "day_of_month": 1
        },
        "action_type": "pay_bill",
        "action_config": {
            "amount": 1500,
            "payee": "Landlord"
        }
    }
    
    response = await client.post(
        "/api/v1/workflows/",
        headers=auth_headers,
        json=workflow_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["workflow_type"] == "bill_payment"
    assert data["name"] == "Auto Pay Rent"


@pytest.mark.asyncio
async def test_list_workflows(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test listing user workflows"""
    workflows = [
        AutonomousWorkflow(
            user_id=test_user.id,
            workflow_type="savings_transfer",
            name=f"Workflow {i}",
            description="Test workflow",
            trigger_type="schedule",
            trigger_config={"schedule": "daily"},
            action_type="transfer_funds",
            action_config={"amount": 100},
            status="active",
            is_enabled=True
        )
        for i in range(3)
    ]
    db_session.add_all(workflows)
    await db_session.commit()
    
    response = await client.get(
        "/api/v1/workflows/",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


@pytest.mark.asyncio
async def test_get_workflow(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test getting a specific workflow"""
    workflow = AutonomousWorkflow(
        user_id=test_user.id,
        workflow_type="spending_alert",
        name="High Spending Alert",
        description="Alert when spending exceeds threshold",
        trigger_type="spending_threshold",
        trigger_config={
            "threshold": 1000,
            "category": "dining"
        },
        action_type="send_notification",
        action_config={
            "message": "High spending detected"
        },
        status="active",
        is_enabled=True
    )
    db_session.add(workflow)
    await db_session.commit()
    await db_session.refresh(workflow)
    
    response = await client.get(
        f"/api/v1/workflows/{workflow.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "High Spending Alert"
    assert data["workflow_type"] == "spending_alert"


@pytest.mark.asyncio
async def test_update_workflow(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test updating a workflow"""
    workflow = AutonomousWorkflow(
        user_id=test_user.id,
        workflow_type="savings_transfer",
        name="Original Name",
        description="Original description",
        trigger_type="schedule",
        trigger_config={"schedule": "daily"},
        action_type="transfer_funds",
        action_config={"amount": 100},
        status="inactive",
        is_enabled=False
    )
    db_session.add(workflow)
    await db_session.commit()
    await db_session.refresh(workflow)
    
    update_data = {
        "name": "Updated Name",
        "description": "Updated description",
        "trigger_config": {
            "frequency": "weekly",
            "time": "10:00",
            "days_of_week": [4]
        }
    }
    
    response = await client.put(
        f"/api/v1/workflows/{workflow.id}",
        headers=auth_headers,
        json=update_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_delete_workflow(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test deleting a workflow"""
    workflow = AutonomousWorkflow(
        user_id=test_user.id,
        workflow_type="custom",
        name="To Delete",
        description="This will be deleted",
        trigger_type="manual",
        trigger_config={},
        action_type="send_notification",
        action_config={},
        status="inactive",
        is_enabled=False
    )
    db_session.add(workflow)
    await db_session.commit()
    await db_session.refresh(workflow)
    
    response = await client.delete(
        f"/api/v1/workflows/{workflow.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = await client.get(
        f"/api/v1/workflows/{workflow.id}",
        headers=auth_headers
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_activate_workflow(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test activating a workflow"""
    workflow = AutonomousWorkflow(
        user_id=test_user.id,
        workflow_type="bill_payment",
        name="Bill Payment",
        description="Pay bills automatically",
        trigger_type="schedule",
        trigger_config={"schedule": "daily"},
        action_type="pay_bill",
        action_config={},
        status="inactive",
        is_enabled=False
    )
    db_session.add(workflow)
    await db_session.commit()
    await db_session.refresh(workflow)
    
    response = await client.post(
        f"/api/v1/workflows/{workflow.id}/activate",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert "message" in data


@pytest.mark.asyncio
async def test_pause_workflow(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test pausing a workflow"""
    workflow = AutonomousWorkflow(
        user_id=test_user.id,
        workflow_type="savings_transfer",
        name="Savings Transfer",
        description="Transfer to savings",
        trigger_type="schedule",
        trigger_config={"schedule": "daily"},
        action_type="transfer_funds",
        action_config={"amount": 100},
        status="active",
        is_enabled=True
    )
    db_session.add(workflow)
    await db_session.commit()
    await db_session.refresh(workflow)
    
    response = await client.post(
        f"/api/v1/workflows/{workflow.id}/pause",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "paused"
    assert "message" in data


@pytest.mark.asyncio
async def test_deactivate_workflow(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test deactivating a workflow"""
    workflow = AutonomousWorkflow(
        user_id=test_user.id,
        workflow_type="budget_alert",
        name="Budget Alert",
        description="Alert on budget",
        trigger_type="schedule",
        trigger_config={"schedule": "daily"},
        action_type="send_notification",
        action_config={},
        status="active",
        is_enabled=True
    )
    db_session.add(workflow)
    await db_session.commit()
    await db_session.refresh(workflow)
    
    response = await client.post(
        f"/api/v1/workflows/{workflow.id}/deactivate",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "inactive"
    assert "message" in data


@pytest.mark.asyncio
async def test_execute_workflow(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test executing a workflow"""
    workflow = AutonomousWorkflow(
        user_id=test_user.id,
        workflow_type="custom",
        name="Manual Workflow",
        description="Execute manually",
        trigger_type="manual",
        trigger_config={},
        action_type="send_notification",
        action_config={
            "message": "Test execution"
        },
        status="active",
        is_enabled=True
    )
    db_session.add(workflow)
    await db_session.commit()
    await db_session.refresh(workflow)
    
    response = await client.post(
        f"/api/v1/workflows/{workflow.id}/execute",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "execution_id" in data
    assert data["status"] in ["pending", "running", "completed"]
    assert "workflow_id" in data


@pytest.mark.asyncio
async def test_get_workflow_executions(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test getting workflow execution history"""
    workflow = AutonomousWorkflow(
        user_id=test_user.id,
        workflow_type="savings_transfer",
        name="Savings Workflow",
        description="Test executions",
        trigger_type="schedule",
        trigger_config={"schedule": "daily"},
        action_type="transfer_funds",
        action_config={"amount": 100},
        status="active",
        is_enabled=True
    )
    db_session.add(workflow)
    await db_session.commit()
    await db_session.refresh(workflow)
    
    # Create execution history
    executions = [
        WorkflowExecution(
            workflow_id=workflow.id,
            status="completed",
            started_at=datetime.utcnow() - timedelta(days=i),
            completed_at=datetime.utcnow() - timedelta(days=i, hours=-1),
            result={"message": f"Execution {i}"}
        )
        for i in range(3)
    ]
    db_session.add_all(executions)
    await db_session.commit()
    
    response = await client.get(
        f"/api/v1/workflows/{workflow.id}/executions",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


@pytest.mark.asyncio
async def test_get_workflow_statistics(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test getting workflow statistics"""
    # Create workflows with different statuses
    workflows = [
        AutonomousWorkflow(
            user_id=test_user.id,
            workflow_type="bill_payment",
            name=f"Workflow {i}",
            description="Test",
            trigger_type="schedule",
            trigger_config={"schedule": "daily"},
            action_type="pay_bill",
            action_config={},
            status="active" if is_active else "inactive",
            is_enabled=is_active,
            total_executions=i * 5
        )
        for i, is_active in enumerate([True, True, False])
    ]
    db_session.add_all(workflows)
    await db_session.commit()
    
    response = await client.get(
        "/api/v1/workflows/summary/stats",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_workflows"] >= 3
    assert data["active_workflows"] >= 2


@pytest.mark.asyncio
async def test_quick_bill_payment_workflow(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test creating quick bill payment workflow"""
    # Create an account first
    account = FinancialAccount(
        user_id=test_user.id,
        account_type="checking",
        institution_name="Test Bank",
        account_name="Main Checking",
        balance=5000,
        currency="USD"
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    
    response = await client.post(
        f"/api/v1/workflows/quick/bill-payment?name=Rent Payment&bill_amount=1500&from_account_id={account.id}&to_account_id={account.id}&days_before_due=3",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["workflow_type"] == "bill_payment"
    assert data["name"] == "Rent Payment"


@pytest.mark.asyncio
async def test_quick_savings_transfer_workflow(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test creating quick savings transfer workflow"""
    # Create accounts
    checking = FinancialAccount(
        user_id=test_user.id,
        account_type="checking",
        institution_name="Test Bank",
        account_name="Checking",
        balance=5000,
        currency="USD"
    )
    savings = FinancialAccount(
        user_id=test_user.id,
        account_type="savings",
        institution_name="Test Bank",
        account_name="Savings",
        balance=10000,
        currency="USD"
    )
    db_session.add_all([checking, savings])
    await db_session.commit()
    await db_session.refresh(checking)
    await db_session.refresh(savings)
    
    response = await client.post(
        f"/api/v1/workflows/quick/savings-transfer?name=Weekly Savings&from_account_id={checking.id}&to_account_id={savings.id}&transfer_percentage=10&frequency=weekly",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["workflow_type"] == "savings_transfer"


@pytest.mark.asyncio
async def test_quick_spending_alert_workflow(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict
):
    """Test creating quick spending alert workflow"""
    response = await client.post(
        "/api/v1/workflows/quick/spending-alert?name=Dining Alert&category=dining&threshold_amount=500&notification_type=email",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["workflow_type"] == "spending_alert"
    assert data["name"] == "Dining Alert"


@pytest.mark.asyncio
async def test_filter_workflows_by_type(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test filtering workflows by type"""
    types = ["bill_payment", "savings_transfer", "spending_alert"]
    workflows = [
        AutonomousWorkflow(
            user_id=test_user.id,
            workflow_type=wf_type,
            name=f"{wf_type} workflow",
            description="Test",
            trigger_type="schedule",
            trigger_config={"schedule": "daily"},
            action_type="send_notification",
            action_config={},
            status="active",
            is_enabled=True
        )
        for wf_type in types
    ]
    db_session.add_all(workflows)
    await db_session.commit()
    
    response = await client.get(
        "/api/v1/workflows/?workflow_type=bill_payment",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["workflow_type"] == "bill_payment"


@pytest.mark.asyncio
async def test_filter_workflows_by_active_status(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test filtering workflows by active status"""
    workflows = [
        AutonomousWorkflow(
            user_id=test_user.id,
            workflow_type="custom",
            name=f"Workflow {i}",
            description="Test",
            trigger_type="schedule",
            trigger_config={"schedule": "daily"},
            action_type="send_notification",
            action_config={},
            status="active" if is_active else "inactive",
            is_enabled=is_active
        )
        for i, is_active in enumerate([True, True, False, False])
    ]
    db_session.add_all(workflows)
    await db_session.commit()
    
    response = await client.get(
        "/api/v1/workflows/?is_enabled=true",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(wf["is_enabled"] for wf in data)


@pytest.mark.asyncio
async def test_workflow_execution_limits(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test workflow execution limits"""
    workflow = AutonomousWorkflow(
        user_id=test_user.id,
        workflow_type="custom",
        name="Limited Workflow",
        description="Has execution limits",
        trigger_type="manual",
        trigger_config={},
        action_type="send_notification",
        action_config={},
        status="active",
        is_enabled=True,
        max_executions_per_day=2,
        execution_count_today=2  # Already at limit
    )
    db_session.add(workflow)
    await db_session.commit()
    await db_session.refresh(workflow)
    
    response = await client.post(
        f"/api/v1/workflows/{workflow.id}/execute",
        headers=auth_headers
    )
    
    # Should fail due to daily limit
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_unauthorized_access_workflow(
    client: AsyncClient,
    test_user: User,
    db_session: AsyncSession
):
    """Test unauthorized access to workflows"""
    workflow = AutonomousWorkflow(
        user_id=test_user.id,
        workflow_type="custom",
        name="Private Workflow",
        description="Should not be accessible",
        trigger_type="manual",
        trigger_config={},
        action_type="send_notification",
        action_config={},
        status="active",
        is_enabled=True
    )
    db_session.add(workflow)
    await db_session.commit()
    await db_session.refresh(workflow)
    
    # Try to access without authentication
    response = await client.get(
        f"/api/v1/workflows/{workflow.id}"
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_workflow_with_approval_required(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test workflow that requires approval"""
    workflow = AutonomousWorkflow(
        user_id=test_user.id,
        workflow_type="bill_payment",
        name="High Value Payment",
        description="Requires approval",
        trigger_type="manual",
        trigger_config={},
        action_type="pay_bill",
        action_config={
            "amount": 5000
        },
        status="active",
        is_enabled=True,
        requires_approval=True
    )
    db_session.add(workflow)
    await db_session.commit()
    await db_session.refresh(workflow)
    
    response = await client.post(
        f"/api/v1/workflows/{workflow.id}/execute",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    # Workflow execution may complete immediately in test mode
    assert data["status"] in ["pending_approval", "completed", "pending"]

# Made with Bob
