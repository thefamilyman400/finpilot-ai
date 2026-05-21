"""
Financial Accounts API Endpoints
CRUD operations and account management
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.account import AccountType
from app.schemas.account import (
    AccountCreate,
    AccountUpdate,
    AccountResponse,
    AccountListResponse,
    AccountSummary,
    AccountSyncRequest,
    AccountSyncResponse,
)
from app.services.account_service import AccountService


router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post(
    "",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new financial account"
)
async def create_account(
    account_data: AccountCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new financial account for the current user.
    
    - **account_type**: Type of account (current, savings, credit_card, investment, loan)
    - **institution_name**: Name of the financial institution
    - **account_name**: Optional custom name for the account
    - **account_number_last4**: Last 4 digits of account number
    - **balance**: Current account balance
    - **currency**: Currency code (default: USD)
    
    **Note**: Credit card accounts require an existing bank account (Current or Savings)
    from the same institution.
    """
    try:
        account = await AccountService.create_account(
            db=db,
            user_id=current_user.id,
            account_data=account_data
        )
        return account
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "",
    response_model=list[AccountResponse],
    summary="List all user accounts"
)
async def list_accounts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    account_type: Optional[AccountType] = Query(None, description="Filter by account type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a list of all accounts for the current user.
    
    Supports filtering by:
    - **account_type**: Filter by specific account type
    - **is_active**: Filter by active/inactive status
    """
    skip = (page - 1) * page_size
    
    accounts, total = await AccountService.get_user_accounts(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=page_size,
        account_type=account_type,
        is_active=is_active
    )
    
    return accounts


@router.get(
    "/summary",
    response_model=AccountSummary,
    summary="Get financial summary"
)
async def get_account_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a comprehensive financial summary across all accounts.
    
    Returns:
    - Total assets and liabilities
    - Net worth
    - Breakdown by account type
    - Account counts and connection status
    """
    summary = await AccountService.get_account_summary(
        db=db,
        user_id=current_user.id
    )
    return summary


@router.get(
    "/{account_id}",
    response_model=AccountResponse,
    summary="Get account details"
)
async def get_account(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific account.
    """
    account = await AccountService.get_account(
        db=db,
        account_id=account_id,
        user_id=current_user.id
    )
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    return account


@router.put(
    "/{account_id}",
    response_model=AccountResponse,
    summary="Update account"
)
async def update_account(
    account_id: UUID,
    account_data: AccountUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing account.
    
    Only provided fields will be updated.
    """
    account = await AccountService.update_account(
        db=db,
        account_id=account_id,
        user_id=current_user.id,
        account_data=account_data
    )
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    return account


@router.delete(
    "/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete account"
)
async def delete_account(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an account (soft delete - sets is_active to False).
    
    This will also affect related transactions.
    """
    success = await AccountService.delete_account(
        db=db,
        account_id=account_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    return None


@router.post(
    "/{account_id}/sync",
    response_model=AccountSyncResponse,
    summary="Sync account data"
)
async def sync_account(
    account_id: UUID,
    sync_request: AccountSyncRequest = AccountSyncRequest(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Synchronize account data from external financial institution.
    
    - **force**: Force sync even if recently synced (default: False)
    
    This will update account balance and import new transactions.
    """
    account = await AccountService.sync_account(
        db=db,
        account_id=account_id,
        user_id=current_user.id,
        force=sync_request.force
    )
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    return AccountSyncResponse(
        account_id=account.id,
        success=True,
        message="Account synced successfully",
        last_synced=account.last_synced,
        transactions_imported=0  # TODO: Implement actual transaction import
    )

# Made with Bob