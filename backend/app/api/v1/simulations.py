"""
Simulations API endpoints
Handles financial simulations and scenario planning
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.simulation import SimulationType, SimulationStatus
from app.schemas.simulation import (
    SimulationCreate,
    SimulationUpdate,
    SimulationResponse,
    SimulationListResponse,
    RetirementSimulationParams,
    InvestmentSimulationParams,
    LoanPayoffSimulationParams,
    BudgetForecastParams,
)
from app.services.simulation_service import simulation_service


router = APIRouter(prefix="/simulations", tags=["Simulations"])


@router.post("/", response_model=SimulationResponse, status_code=status.HTTP_201_CREATED)
async def create_simulation(
    simulation_data: SimulationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new financial simulation
    
    - **name**: Simulation name
    - **simulation_type**: Type of simulation (retirement, investment, etc.)
    - **input_parameters**: Simulation parameters
    """
    try:
        simulation = await simulation_service.create_simulation(
            db=db,
            user_id=current_user.id,
            simulation_data=simulation_data,
        )
        return simulation
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create simulation: {str(e)}"
        )


@router.get("/{simulation_id}", response_model=SimulationResponse)
async def get_simulation(
    simulation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific simulation by ID"""
    simulation = await simulation_service.get_simulation(db, simulation_id, current_user.id)
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    return simulation


@router.get("/", response_model=List[SimulationResponse])
async def list_simulations(
    simulation_type: Optional[SimulationType] = Query(None),
    status_filter: Optional[SimulationStatus] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List user's simulations with optional filters
    
    - **simulation_type**: Filter by simulation type
    - **status**: Filter by execution status
    - **skip**: Number of simulations to skip
    - **limit**: Maximum number of simulations to return
    """
    simulations = await simulation_service.list_simulations(
        db=db,
        user_id=current_user.id,
        simulation_type=simulation_type,
        status=status_filter,
        skip=skip,
        limit=limit,
    )
    return simulations


@router.put("/{simulation_id}", response_model=SimulationResponse)
async def update_simulation(
    simulation_id: UUID,
    update_data: SimulationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update simulation metadata"""
    simulation = await simulation_service.update_simulation(
        db=db,
        simulation_id=simulation_id,
        user_id=current_user.id,
        update_data=update_data,
    )
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    return simulation


@router.delete("/{simulation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_simulation(
    simulation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a simulation"""
    success = await simulation_service.delete_simulation(
        db=db,
        simulation_id=simulation_id,
        user_id=current_user.id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    return None


@router.post("/{simulation_id}/run", response_model=SimulationResponse)
async def run_simulation(
    simulation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute a financial simulation
    
    Runs the simulation with the configured parameters and returns results including:
    - Projections and forecasts
    - Best/worst case scenarios
    - Success probabilities
    - Recommendations
    """
    try:
        simulation = await simulation_service.run_simulation(
            db=db,
            simulation_id=simulation_id,
            user_id=current_user.id,
        )
        return simulation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulation execution failed: {str(e)}"
        )


# Convenience endpoints for specific simulation types

@router.post("/retirement/quick", response_model=SimulationResponse)
async def quick_retirement_simulation(
    params: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Quick retirement planning simulation
    
    Creates and runs a retirement simulation with provided parameters
    """
    simulation_data = SimulationCreate(
        name=f"Retirement Plan - {params.get('current_age')} to {params.get('retirement_age')}",
        simulation_type=SimulationType.RETIREMENT,
        parameters=params
    )
    
    simulation = await simulation_service.create_simulation(db, current_user.id, simulation_data)
    simulation = await simulation_service.run_simulation(db, simulation.id, current_user.id)
    return simulation


@router.post("/investment/quick", response_model=SimulationResponse)
async def quick_investment_simulation(
    params: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Quick investment scenario simulation
    
    Creates and runs an investment simulation with provided parameters
    """
    simulation_data = SimulationCreate(
        name=f"Investment Plan - {params.get('years')} years",
        simulation_type=SimulationType.INVESTMENT,
        parameters=params
    )
    
    simulation = await simulation_service.create_simulation(db, current_user.id, simulation_data)
    simulation = await simulation_service.run_simulation(db, simulation.id, current_user.id)
    return simulation


@router.post("/loan-payoff/quick", response_model=SimulationResponse)
async def quick_loan_payoff_simulation(
    params: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Quick loan payoff simulation
    
    Calculates loan payoff timeline with optional extra payments
    """
    simulation_data = SimulationCreate(
        name=f"Loan Payoff - ${params.get('loan_amount', 0):,.0f}",
        simulation_type=SimulationType.LOAN_PAYOFF,
        parameters=params
    )
    
    simulation = await simulation_service.create_simulation(db, current_user.id, simulation_data)
    simulation = await simulation_service.run_simulation(db, simulation.id, current_user.id)
    return simulation


@router.post("/budget-forecast/quick", response_model=SimulationResponse)
async def quick_budget_forecast(
    params: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Quick budget forecast simulation
    
    Projects income, expenses, and savings over time
    """
    simulation_data = SimulationCreate(
        name=f"Budget Forecast - {params.get('months', 12)} months",
        simulation_type=SimulationType.BUDGET_FORECAST,
        parameters=params
    )
    
    simulation = await simulation_service.create_simulation(db, current_user.id, simulation_data)
    simulation = await simulation_service.run_simulation(db, simulation.id, current_user.id)
    return simulation


# Made with Bob