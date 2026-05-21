"""
Tests for simulation endpoints and service
"""
import pytest
from decimal import Decimal
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.simulation import FinancialSimulation


@pytest.mark.asyncio
async def test_create_retirement_simulation(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test creating a retirement simulation"""
    simulation_data = {
        "simulation_type": "retirement",
        "name": "My Retirement Plan",
        "description": "Planning for retirement at 65",
        "parameters": {
            "current_age": 30,
            "retirement_age": 65,
            "current_savings": 50000,
            "monthly_contribution": 1000,
            "expected_return": 7.0,
            "inflation_rate": 3.0
        }
    }
    
    response = await client.post(
        "/api/v1/simulations/",
        headers=auth_headers,
        json=simulation_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["simulation_type"] == "retirement"
    assert data["name"] == "My Retirement Plan"
    assert data["status"] == "draft"


@pytest.mark.asyncio
async def test_create_investment_simulation(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict
):
    """Test creating an investment simulation"""
    simulation_data = {
        "simulation_type": "investment",
        "name": "Stock Portfolio Growth",
        "description": "Projecting portfolio growth",
        "parameters": {
            "initial_investment": 10000,
            "monthly_contribution": 500,
            "years": 10,
            "expected_return": 8.0,
            "risk_level": "moderate"
        }
    }
    
    response = await client.post(
        "/api/v1/simulations/",
        headers=auth_headers,
        json=simulation_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["simulation_type"] == "investment"


@pytest.mark.asyncio
async def test_list_simulations(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test listing user simulations"""
    simulations = [
        FinancialSimulation(
            user_id=test_user.id,
            simulation_type="retirement",
            name=f"Simulation {i}",
            description="Test simulation",
            parameters={"test": "data"},
            status="draft"
        )
        for i in range(3)
    ]
    db_session.add_all(simulations)
    await db_session.commit()
    
    response = await client.get(
        "/api/v1/simulations/",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


@pytest.mark.asyncio
async def test_get_simulation(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test getting a specific simulation"""
    simulation = FinancialSimulation(
        user_id=test_user.id,
        simulation_type="loan_payoff",
        name="Mortgage Payoff",
        description="Calculate mortgage payoff scenarios",
        parameters={
            "loan_amount": 300000,
            "interest_rate": 4.5,
            "term_years": 30
        },
        status="completed",
        results={
            "total_interest": 247220,
            "monthly_payment": 1520
        }
    )
    db_session.add(simulation)
    await db_session.commit()
    await db_session.refresh(simulation)
    
    response = await client.get(
        f"/api/v1/simulations/{simulation.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Mortgage Payoff"
    assert data["simulation_type"] == "loan_payoff"


@pytest.mark.asyncio
async def test_update_simulation(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test updating a simulation"""
    simulation = FinancialSimulation(
        user_id=test_user.id,
        simulation_type="budget_forecast",
        name="Original Name",
        description="Original description",
        parameters={"test": "data"},
        status="draft"
    )
    db_session.add(simulation)
    await db_session.commit()
    await db_session.refresh(simulation)
    
    update_data = {
        "name": "Updated Name",
        "description": "Updated description",
        "parameters": {
            "monthly_income": 5000,
            "monthly_expenses": 3500
        }
    }
    
    response = await client.put(
        f"/api/v1/simulations/{simulation.id}",
        headers=auth_headers,
        json=update_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_delete_simulation(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test deleting a simulation"""
    simulation = FinancialSimulation(
        user_id=test_user.id,
        simulation_type="investment",
        name="To Delete",
        description="This will be deleted",
        parameters={"test": "data"},
        status="draft"
    )
    db_session.add(simulation)
    await db_session.commit()
    await db_session.refresh(simulation)
    
    response = await client.delete(
        f"/api/v1/simulations/{simulation.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = await client.get(
        f"/api/v1/simulations/{simulation.id}",
        headers=auth_headers
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_run_simulation(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test running a simulation"""
    simulation = FinancialSimulation(
        user_id=test_user.id,
        simulation_type="retirement",
        name="Retirement Plan",
        description="Test retirement simulation",
        parameters={
            "current_age": 30,
            "retirement_age": 65,
            "current_savings": 50000,
            "monthly_contribution": 1000,
            "expected_return": 7.0
        },
        status="draft"
    )
    db_session.add(simulation)
    await db_session.commit()
    await db_session.refresh(simulation)
    
    response = await client.post(
        f"/api/v1/simulations/{simulation.id}/run",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert "results" in data
    assert data["results"] is not None


@pytest.mark.asyncio
async def test_quick_retirement_simulation(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict
):
    """Test quick retirement simulation"""
    params = {
        "current_age": 35,
        "retirement_age": 65,
        "current_savings": 100000,
        "monthly_contribution": 1500,
        "expected_return": 7.0,
        "inflation_rate": 3.0
    }
    
    response = await client.post(
        "/api/v1/simulations/retirement/quick",
        headers=auth_headers,
        json=params
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["results"] is not None


@pytest.mark.asyncio
async def test_quick_investment_simulation(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict
):
    """Test quick investment simulation"""
    params = {
        "initial_investment": 10000,
        "monthly_contribution": 500,
        "years": 10,
        "expected_return": 8.0,
        "risk_level": "moderate"
    }
    
    response = await client.post(
        "/api/v1/simulations/investment/quick",
        headers=auth_headers,
        json=params
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["results"] is not None


@pytest.mark.asyncio
async def test_quick_loan_payoff_simulation(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict
):
    """Test quick loan payoff simulation"""
    params = {
        "loan_amount": 250000,
        "interest_rate": 4.0,
        "term_years": 30,
        "extra_payment": 200
    }
    
    response = await client.post(
        "/api/v1/simulations/loan-payoff/quick",
        headers=auth_headers,
        json=params
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["results"] is not None


@pytest.mark.asyncio
async def test_quick_budget_forecast_simulation(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict
):
    """Test quick budget forecast simulation"""
    params = {
        "monthly_income": 6000,
        "monthly_expenses": 4500,
        "months": 12,
        "income_growth": 3.0,
        "expense_growth": 2.0
    }
    
    response = await client.post(
        "/api/v1/simulations/budget-forecast/quick",
        headers=auth_headers,
        json=params
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["results"] is not None


@pytest.mark.asyncio
async def test_filter_simulations_by_type(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test filtering simulations by type"""
    types = ["retirement", "investment", "loan_payoff"]
    simulations = [
        FinancialSimulation(
            user_id=test_user.id,
            simulation_type=sim_type,
            name=f"{sim_type} simulation",
            description="Test",
            parameters={"test": "data"},
            status="draft"
        )
        for sim_type in types
    ]
    db_session.add_all(simulations)
    await db_session.commit()
    
    response = await client.get(
        "/api/v1/simulations/?simulation_type=retirement",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["simulation_type"] == "retirement"


@pytest.mark.asyncio
async def test_filter_simulations_by_status(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test filtering simulations by status"""
    statuses = ["draft", "running", "completed"]
    simulations = [
        FinancialSimulation(
            user_id=test_user.id,
            simulation_type="investment",
            name=f"Simulation {status}",
            description="Test",
            parameters={"test": "data"},
            status=status
        )
        for status in statuses
    ]
    db_session.add_all(simulations)
    await db_session.commit()
    
    response = await client.get(
        "/api/v1/simulations/?status=completed",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "completed"


@pytest.mark.asyncio
async def test_simulation_with_monte_carlo(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test simulation with Monte Carlo analysis"""
    simulation = FinancialSimulation(
        user_id=test_user.id,
        simulation_type="investment",
        name="Monte Carlo Investment",
        description="Investment with uncertainty",
        parameters={
            "initial_investment": 10000,
            "monthly_contribution": 500,
            "years": 10,
            "expected_return": 8.0,
            "volatility": 15.0,
            "simulations": 1000
        },
        status="draft"
    )
    db_session.add(simulation)
    await db_session.commit()
    await db_session.refresh(simulation)
    
    response = await client.post(
        f"/api/v1/simulations/{simulation.id}/run",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["results"] is not None


@pytest.mark.asyncio
async def test_invalid_simulation_parameters(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict
):
    """Test creating simulation with invalid parameters"""
    simulation_data = {
        "simulation_type": "retirement",
        "name": "Invalid Simulation",
        "parameters": {
            "current_age": 70,  # Invalid: older than retirement age
            "retirement_age": 65,
            "current_savings": -1000  # Invalid: negative savings
        }
    }
    
    response = await client.post(
        "/api/v1/simulations/",
        headers=auth_headers,
        json=simulation_data
    )
    
    # API accepts any parameters and creates simulation in draft status
    # Validation happens when running the simulation
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "draft"


@pytest.mark.asyncio
async def test_unauthorized_access_simulation(
    client: AsyncClient,
    test_user: User,
    db_session: AsyncSession
):
    """Test unauthorized access to simulations"""
    simulation = FinancialSimulation(
        user_id=test_user.id,
        simulation_type="retirement",
        name="Private Simulation",
        description="Should not be accessible",
        parameters={"test": "data"},
        status="draft"
    )
    db_session.add(simulation)
    await db_session.commit()
    await db_session.refresh(simulation)
    
    # Try to access without authentication
    response = await client.get(
        f"/api/v1/simulations/{simulation.id}"
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_simulation_results_persistence(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test that simulation results are persisted"""
    simulation = FinancialSimulation(
        user_id=test_user.id,
        simulation_type="loan_payoff",
        name="Loan Analysis",
        description="Test persistence",
        parameters={
            "loan_amount": 200000,
            "interest_rate": 3.5,
            "term_years": 30
        },
        status="draft"
    )
    db_session.add(simulation)
    await db_session.commit()
    await db_session.refresh(simulation)
    
    # Run simulation
    run_response = await client.post(
        f"/api/v1/simulations/{simulation.id}/run",
        headers=auth_headers
    )
    assert run_response.status_code == 200
    
    # Get simulation again to verify results are saved
    get_response = await client.get(
        f"/api/v1/simulations/{simulation.id}",
        headers=auth_headers
    )
    
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["status"] == "completed"
    assert data["results"] is not None

# Made with Bob
