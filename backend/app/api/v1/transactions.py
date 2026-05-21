"""
Transaction API Endpoints
CRUD operations and transaction analytics
"""
from datetime import date, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.transaction import TransactionType, TransactionCategory
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionFilters,
    TransactionListResponse,
    TransactionAnalytics,
    BulkCategorizeRequest,
    BulkCategorizeResponse,
)
from app.services.transaction_service import TransactionService


router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new transaction"
)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new transaction for a specific account.
    
    - **account_id**: ID of the account this transaction belongs to
    - **transaction_date**: Date of the transaction
    - **amount**: Transaction amount
    - **transaction_type**: Type (debit/credit)
    - **category**: Optional category for organization
    - **merchant_name**: Optional merchant/vendor name
    - **description**: Optional description
    - **is_recurring**: Whether this is a recurring transaction
    - **tags**: Optional list of tags
    - **notes**: Optional notes
    """
    try:
        transaction = await TransactionService.create_transaction(
            db=db,
            user_id=current_user.id,
            transaction_data=transaction_data
        )
        return transaction
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=TransactionListResponse,
    summary="List transactions with filters"
)
async def list_transactions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    account_id: Optional[UUID] = Query(None, description="Filter by account"),
    transaction_type: Optional[TransactionType] = Query(None, description="Filter by type"),
    category: Optional[TransactionCategory] = Query(None, description="Filter by category"),
    merchant_name: Optional[str] = Query(None, description="Filter by merchant"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    min_amount: Optional[float] = Query(None, description="Minimum amount"),
    max_amount: Optional[float] = Query(None, description="Maximum amount"),
    is_recurring: Optional[bool] = Query(None, description="Filter recurring"),
    search: Optional[str] = Query(None, description="Search in description/merchant"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a paginated list of transactions with various filters.
    
    Supports filtering by:
    - Account, type, category, merchant
    - Date range
    - Amount range
    - Recurring status
    - Text search
    """
    skip = (page - 1) * page_size
    
    filters = TransactionFilters(
        account_id=account_id,
        transaction_type=transaction_type,
        category=category,
        merchant_name=merchant_name,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount,
        is_recurring=is_recurring,
        search=search
    )
    
    transactions, total, total_income, total_expenses = await TransactionService.get_transactions(
        db=db,
        user_id=current_user.id,
        filters=filters,
        skip=skip,
        limit=page_size
    )
    
    return TransactionListResponse(
        transactions=transactions,
        total=total,
        page=page,
        page_size=page_size,
        total_income=total_income,
        total_expenses=total_expenses,
        net_amount=total_income - total_expenses
    )


@router.get(
    "/analytics",
    response_model=TransactionAnalytics,
    summary="Get transaction analytics"
)
async def get_transaction_analytics(
    start_date: Optional[date] = Query(None, description="Start date (default: 30 days ago)"),
    end_date: Optional[date] = Query(None, description="End date (default: today)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive transaction analytics for a date range.
    
    Returns:
    - Income and expense totals
    - Category breakdowns
    - Top merchants
    - Daily/monthly trends
    - Recurring transaction summary
    - Average spending metrics
    
    Default date range is last 30 days if not specified.
    """
    # Set default date range if not provided
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    analytics = await TransactionService.get_analytics(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    return analytics


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Get transaction details"
)
async def get_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific transaction.
    """
    transaction = await TransactionService.get_transaction(
        db=db,
        transaction_id=transaction_id,
        user_id=current_user.id
    )
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return transaction


@router.put(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Update transaction"
)
async def update_transaction(
    transaction_id: UUID,
    transaction_data: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing transaction.
    
    Only provided fields will be updated.
    """
    transaction = await TransactionService.update_transaction(
        db=db,
        transaction_id=transaction_id,
        user_id=current_user.id,
        transaction_data=transaction_data
    )
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return transaction


@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete transaction"
)
async def delete_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a transaction permanently.
    """
    success = await TransactionService.delete_transaction(
        db=db,
        transaction_id=transaction_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return None


@router.post(
    "/categorize",
    response_model=BulkCategorizeResponse,
    summary="Bulk categorize transactions"
)
async def bulk_categorize_transactions(
    categorize_request: BulkCategorizeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Categorize multiple transactions at once.
    
    - **transaction_ids**: List of transaction IDs to categorize
    - **category**: Category to assign to all transactions
    
    Returns the number of successfully updated transactions and any failed IDs.
    """
    updated_count, failed_ids = await TransactionService.bulk_categorize(
        db=db,
        user_id=current_user.id,
        transaction_ids=categorize_request.transaction_ids,
        category=categorize_request.category
    )
    
    success = len(failed_ids) == 0
    message = f"Successfully categorized {updated_count} transaction(s)"
    
    if failed_ids:
        message += f", {len(failed_ids)} failed"
    
    return BulkCategorizeResponse(
        success=success,
        updated_count=updated_count,
        failed_ids=failed_ids,
        message=message
    )

# Made with Bob