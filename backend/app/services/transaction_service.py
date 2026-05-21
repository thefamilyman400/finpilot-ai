"""
Transaction Service
Business logic for transaction operations
"""
from datetime import datetime, date, timedelta
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from collections import defaultdict

from sqlalchemy import select, func, and_, or_, desc, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction, TransactionType, TransactionCategory
from app.models.account import FinancialAccount
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionFilters,
    TransactionAnalytics,
    CategoryStatistics,
)


class TransactionService:
    """Service for managing financial transactions"""

    @staticmethod
    async def create_transaction(
        db: AsyncSession,
        user_id: UUID,
        transaction_data: TransactionCreate
    ) -> Transaction:
        """
        Create a new transaction
        
        Args:
            db: Database session
            user_id: User ID
            transaction_data: Transaction creation data
            
        Returns:
            Created transaction
        """
        # Verify account belongs to user
        account_result = await db.execute(
            select(FinancialAccount).where(
                and_(
                    FinancialAccount.id == transaction_data.account_id,
                    FinancialAccount.user_id == user_id
                )
            )
        )
        account = account_result.scalar_one_or_none()
        
        if not account:
            raise ValueError("Account not found or does not belong to user")
        
        transaction = Transaction(
            account_id=transaction_data.account_id,
            user_id=user_id,
            transaction_date=transaction_data.transaction_date,
            description=transaction_data.description,
            amount=transaction_data.amount,
            transaction_type=transaction_data.transaction_type,
            category=transaction_data.category,
            merchant_name=transaction_data.merchant_name,
            is_recurring=transaction_data.is_recurring,
            tags=transaction_data.tags,
            notes=transaction_data.notes,
        )
        
        db.add(transaction)
        
        # Update account balance
        current_balance = float(account.balance) if account.balance else 0.0
        if transaction_data.transaction_type == TransactionType.CREDIT:
            # Credit increases balance
            account.balance = current_balance + transaction_data.amount
        else:
            # Debit decreases balance
            account.balance = current_balance - transaction_data.amount
        
        await db.commit()
        await db.refresh(transaction)
        
        return transaction

    @staticmethod
    async def get_transaction(
        db: AsyncSession,
        transaction_id: UUID,
        user_id: UUID
    ) -> Optional[Transaction]:
        """
        Get a specific transaction by ID
        
        Args:
            db: Database session
            transaction_id: Transaction ID
            user_id: User ID (for authorization)
            
        Returns:
            Transaction if found and belongs to user, None otherwise
        """
        result = await db.execute(
            select(Transaction).where(
                and_(
                    Transaction.id == transaction_id,
                    Transaction.user_id == user_id
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_transactions(
        db: AsyncSession,
        user_id: UUID,
        filters: TransactionFilters,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[Transaction], int, float, float]:
        """
        Get transactions with filters and pagination
        
        Args:
            db: Database session
            user_id: User ID
            filters: Transaction filters
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (transactions list, total count, total income, total expenses)
        """
        # Build base query
        query = select(Transaction).where(Transaction.user_id == user_id)
        
        # Apply filters
        if filters.account_id:
            query = query.where(Transaction.account_id == filters.account_id)
        
        if filters.transaction_type:
            query = query.where(Transaction.transaction_type == filters.transaction_type)
        
        if filters.category:
            query = query.where(Transaction.category == filters.category)
        
        if filters.merchant_name:
            query = query.where(Transaction.merchant_name.ilike(f"%{filters.merchant_name}%"))
        
        if filters.start_date:
            query = query.where(Transaction.transaction_date >= filters.start_date)
        
        if filters.end_date:
            query = query.where(Transaction.transaction_date <= filters.end_date)
        
        if filters.min_amount:
            query = query.where(Transaction.amount >= filters.min_amount)
        
        if filters.max_amount:
            query = query.where(Transaction.amount <= filters.max_amount)
        
        if filters.is_recurring is not None:
            query = query.where(Transaction.is_recurring == filters.is_recurring)
        
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                or_(
                    Transaction.description.ilike(search_term),
                    Transaction.merchant_name.ilike(search_term)
                )
            )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()
        
        # Calculate totals using case statements to avoid cartesian product
        totals_query = select(
            func.sum(case((Transaction.transaction_type == TransactionType.CREDIT, Transaction.amount), else_=0)).label("income"),
            func.sum(case((Transaction.transaction_type == TransactionType.DEBIT, Transaction.amount), else_=0)).label("expenses")
        ).where(Transaction.user_id == user_id)
        
        # Apply same filters as main query
        if filters.account_id:
            totals_query = totals_query.where(Transaction.account_id == filters.account_id)
        if filters.transaction_type:
            totals_query = totals_query.where(Transaction.transaction_type == filters.transaction_type)
        if filters.category:
            totals_query = totals_query.where(Transaction.category == filters.category)
        if filters.merchant_name:
            totals_query = totals_query.where(Transaction.merchant_name.ilike(f"%{filters.merchant_name}%"))
        if filters.start_date:
            totals_query = totals_query.where(Transaction.transaction_date >= filters.start_date)
        if filters.end_date:
            totals_query = totals_query.where(Transaction.transaction_date <= filters.end_date)
        if filters.min_amount is not None:
            totals_query = totals_query.where(Transaction.amount >= filters.min_amount)
        if filters.max_amount is not None:
            totals_query = totals_query.where(Transaction.amount <= filters.max_amount)
        if filters.search:
            search_term = f"%{filters.search}%"
            totals_query = totals_query.where(
                or_(
                    Transaction.description.ilike(search_term),
                    Transaction.merchant_name.ilike(search_term)
                )
            )
        
        totals_result = await db.execute(totals_query)
        totals = totals_result.one()
        
        total_income = float(totals.income or 0)
        total_expenses = float(totals.expenses or 0)
        
        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(desc(Transaction.transaction_date))
        result = await db.execute(query)
        transactions = result.scalars().all()
        
        return list(transactions), total, total_income, total_expenses

    @staticmethod
    async def update_transaction(
        db: AsyncSession,
        transaction_id: UUID,
        user_id: UUID,
        transaction_data: TransactionUpdate
    ) -> Optional[Transaction]:
        """
        Update an existing transaction
        
        Args:
            db: Database session
            transaction_id: Transaction ID
            user_id: User ID (for authorization)
            transaction_data: Update data
            
        Returns:
            Updated transaction if found, None otherwise
        """
        transaction = await TransactionService.get_transaction(db, transaction_id, user_id)
        
        if not transaction:
            return None
        
        # Update only provided fields
        update_data = transaction_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(transaction, field, value)
        
        await db.commit()
        await db.refresh(transaction)
        
        return transaction

    @staticmethod
    async def delete_transaction(
        db: AsyncSession,
        transaction_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Delete a transaction
        
        Args:
            db: Database session
            transaction_id: Transaction ID
            user_id: User ID (for authorization)
            
        Returns:
            True if deleted, False if not found
        """
        transaction = await TransactionService.get_transaction(db, transaction_id, user_id)
        
        if not transaction:
            return False
        
        await db.delete(transaction)
        await db.commit()
        
        return True

    @staticmethod
    async def bulk_categorize(
        db: AsyncSession,
        user_id: UUID,
        transaction_ids: List[UUID],
        category: TransactionCategory
    ) -> tuple[int, List[UUID]]:
        """
        Bulk categorize multiple transactions
        
        Args:
            db: Database session
            user_id: User ID
            transaction_ids: List of transaction IDs
            category: Category to assign
            
        Returns:
            Tuple of (updated count, failed IDs)
        """
        updated_count = 0
        failed_ids = []
        
        for transaction_id in transaction_ids:
            transaction = await TransactionService.get_transaction(db, transaction_id, user_id)
            
            if transaction:
                transaction.category = category
                updated_count += 1
            else:
                failed_ids.append(transaction_id)
        
        await db.commit()
        
        return updated_count, failed_ids

    @staticmethod
    async def get_analytics(
        db: AsyncSession,
        user_id: UUID,
        start_date: date,
        end_date: date
    ) -> TransactionAnalytics:
        """
        Get transaction analytics for a date range
        
        Args:
            db: Database session
            user_id: User ID
            start_date: Start date
            end_date: End date
            
        Returns:
            Transaction analytics
        """
        # Get all transactions in date range
        result = await db.execute(
            select(Transaction).where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date
                )
            )
        )
        transactions = result.scalars().all()
        
        # Initialize analytics
        analytics = TransactionAnalytics(
            start_date=start_date,
            end_date=end_date,
            transaction_count=len(transactions)
        )
        
        # Calculate totals and breakdowns
        spending_by_category = defaultdict(float)
        income_by_category = defaultdict(float)
        merchant_totals = defaultdict(float)
        daily_totals = defaultdict(lambda: {"income": 0.0, "expenses": 0.0})
        
        for txn in transactions:
            amount = float(txn.amount)
            
            if txn.transaction_type == TransactionType.CREDIT:
                analytics.total_income += amount
                if txn.category:
                    income_by_category[txn.category.value] += amount
            else:
                analytics.total_expenses += amount
                if txn.category:
                    spending_by_category[txn.category.value] += amount
            
            # Merchant totals
            if txn.merchant_name:
                merchant_totals[txn.merchant_name] += amount
            
            # Daily totals
            date_key = txn.transaction_date.isoformat()
            if txn.transaction_type == TransactionType.CREDIT:
                daily_totals[date_key]["income"] += amount
            else:
                daily_totals[date_key]["expenses"] += amount
            
            # Recurring transactions
            if txn.is_recurring:
                analytics.recurring_count += 1
                analytics.recurring_total += amount
        
        # Calculate net amount and averages
        analytics.net_amount = analytics.total_income - analytics.total_expenses
        
        if analytics.transaction_count > 0:
            analytics.avg_transaction_amount = (
                analytics.total_income + analytics.total_expenses
            ) / analytics.transaction_count
        
        days_in_period = (end_date - start_date).days + 1
        if days_in_period > 0:
            analytics.avg_daily_spending = analytics.total_expenses / days_in_period
        
        # Convert dictionaries to proper format
        analytics.spending_by_category = {k: v for k, v in spending_by_category.items()}
        analytics.income_by_category = {k: v for k, v in income_by_category.items()}
        
        # Top merchants
        analytics.top_merchants = [
            {"merchant": merchant, "total": float(total)}
            for merchant, total in sorted(
                merchant_totals.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        ]
        
        # Daily totals
        analytics.daily_totals = [
            {
                "date": date_str,
                "income": float(totals["income"]),
                "expenses": float(totals["expenses"]),
                "net": float(totals["income"] - totals["expenses"])
            }
            for date_str, totals in sorted(daily_totals.items())
        ]
        
        return analytics

# Made with Bob