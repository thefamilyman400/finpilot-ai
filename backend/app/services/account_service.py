"""
Account Service
Business logic for financial account operations
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from decimal import Decimal

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import FinancialAccount, AccountType, ConnectionStatus
from app.schemas.account import (
    AccountCreate,
    AccountUpdate,
    AccountSummary,
)


class AccountService:
    """Service for managing financial accounts"""

    @staticmethod
    async def create_account(
        db: AsyncSession,
        user_id: UUID,
        account_data: AccountCreate
    ) -> FinancialAccount:
        """
        Create a new financial account for a user
        
        Args:
            db: Database session
            user_id: User ID
            account_data: Account creation data
            
        Returns:
            Created account
            
        Raises:
            ValueError: If credit card is being created without a bank account from same institution
        """
        # Validation: Credit card requires a bank account from the same institution
        if account_data.account_type == AccountType.CREDIT_CARD:
            # Check if user has a bank account (CURRENT or SAVINGS) from the same institution
            result = await db.execute(
                select(FinancialAccount).where(
                    and_(
                        FinancialAccount.user_id == user_id,
                        FinancialAccount.institution_name.ilike(account_data.institution_name),
                        FinancialAccount.account_type.in_([AccountType.CURRENT, AccountType.SAVINGS]),
                        FinancialAccount.is_active == True
                    )
                )
            )
            bank_account = result.scalar_one_or_none()
            
            if not bank_account:
                raise ValueError(
                    f"Cannot create credit card account. "
                    f"Please create a bank account (Current or Savings) for {account_data.institution_name} first."
                )
        
        # Prepare account data
        account_dict = {
            'user_id': user_id,
            'account_type': account_data.account_type,
            'institution_name': account_data.institution_name,
            'account_name': account_data.account_name,
            'account_number_last4': account_data.account_number_last4,
            'balance': account_data.balance,
            'currency': account_data.currency,
            'connection_status': ConnectionStatus.MANUAL,
        }
        
        # Add loan-specific fields if provided
        if account_data.account_type == AccountType.LOAN:
            account_dict['loan_principal'] = account_data.loan_principal
            account_dict['loan_outstanding'] = account_data.loan_outstanding
            account_dict['interest_rate'] = account_data.interest_rate
            account_dict['loan_tenure_months'] = account_data.loan_tenure_months
            account_dict['remaining_tenure_months'] = account_data.remaining_tenure_months
            account_dict['loan_start_date'] = account_data.loan_start_date
            account_dict['total_interest_paid'] = account_data.total_interest_paid
            account_dict['total_principal_paid'] = account_data.total_principal_paid
            
            # Auto-calculate EMI if not provided
            if (account_data.loan_principal and
                account_data.interest_rate and
                account_data.loan_tenure_months and
                not account_data.emi_amount):
                
                principal = account_data.loan_principal
                annual_rate = account_data.interest_rate / 100
                monthly_rate = annual_rate / 12
                months = account_data.loan_tenure_months
                
                if monthly_rate > 0:
                    emi = principal * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
                    account_dict['emi_amount'] = round(emi, 2)
                else:
                    account_dict['emi_amount'] = round(principal / months, 2)
            else:
                account_dict['emi_amount'] = account_data.emi_amount
        
        account = FinancialAccount(**account_dict)
        db.add(account)
        await db.commit()
        await db.refresh(account)
        
        return account

    @staticmethod
    async def get_account(
        db: AsyncSession,
        account_id: UUID,
        user_id: UUID
    ) -> Optional[FinancialAccount]:
        """
        Get a specific account by ID
        
        Args:
            db: Database session
            account_id: Account ID
            user_id: User ID (for authorization)
            
        Returns:
            Account if found and belongs to user, None otherwise
        """
        result = await db.execute(
            select(FinancialAccount).where(
                and_(
                    FinancialAccount.id == account_id,
                    FinancialAccount.user_id == user_id
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_accounts(
        db: AsyncSession,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
        account_type: Optional[AccountType] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[FinancialAccount], int]:
        """
        Get all accounts for a user with pagination and filters
        
        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            account_type: Filter by account type
            is_active: Filter by active status
            
        Returns:
            Tuple of (accounts list, total count)
        """
        # Build query with filters
        query = select(FinancialAccount).where(FinancialAccount.user_id == user_id)
        
        if account_type:
            query = query.where(FinancialAccount.account_type == account_type)
        
        if is_active is not None:
            query = query.where(FinancialAccount.is_active == is_active)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()
        
        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(FinancialAccount.created_at.desc())
        result = await db.execute(query)
        accounts = result.scalars().all()
        
        return list(accounts), total

    @staticmethod
    async def update_account(
        db: AsyncSession,
        account_id: UUID,
        user_id: UUID,
        account_data: AccountUpdate
    ) -> Optional[FinancialAccount]:
        """
        Update an existing account
        
        Args:
            db: Database session
            account_id: Account ID
            user_id: User ID (for authorization)
            account_data: Update data
            
        Returns:
            Updated account if found, None otherwise
        """
        account = await AccountService.get_account(db, account_id, user_id)
        
        if not account:
            return None
        
        # Update only provided fields
        update_data = account_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(account, field, value)
        
        await db.commit()
        await db.refresh(account)
        
        return account

    @staticmethod
    async def delete_account(
        db: AsyncSession,
        account_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Delete an account (soft delete by setting is_active to False)
        
        Args:
            db: Database session
            account_id: Account ID
            user_id: User ID (for authorization)
            
        Returns:
            True if deleted, False if not found
        """
        account = await AccountService.get_account(db, account_id, user_id)
        
        if not account:
            return False
        
        account.is_active = False
        await db.commit()
        
        return True

    @staticmethod
    async def sync_account(
        db: AsyncSession,
        account_id: UUID,
        user_id: UUID,
        force: bool = False
    ) -> Optional[FinancialAccount]:
        """
        Sync account data from external service
        
        Args:
            db: Database session
            account_id: Account ID
            user_id: User ID (for authorization)
            force: Force sync even if recently synced
            
        Returns:
            Updated account if found, None otherwise
        """
        account = await AccountService.get_account(db, account_id, user_id)
        
        if not account:
            return None
        
        # Check if sync is needed
        if not force and not account.needs_sync:
            return account
        
        # TODO: Implement actual sync logic with external services (Plaid, etc.)
        # For now, just update the last_synced timestamp
        account.last_synced = datetime.utcnow()
        account.connection_status = ConnectionStatus.CONNECTED
        
        await db.commit()
        await db.refresh(account)
        
        return account

    @staticmethod
    async def get_account_summary(
        db: AsyncSession,
        user_id: UUID
    ) -> AccountSummary:
        """
        Get financial summary across all user accounts
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Account summary with aggregated data
        """
        # Get all active accounts
        result = await db.execute(
            select(FinancialAccount).where(
                and_(
                    FinancialAccount.user_id == user_id,
                    FinancialAccount.is_active == True
                )
            )
        )
        accounts = result.scalars().all()
        
        # Initialize summary
        summary = AccountSummary(
            total_accounts=len(accounts),
            active_accounts=len(accounts),
        )
        
        # Initialize accounts_by_type dict
        accounts_by_type = {}
        
        # Calculate balances by account type
        for account in accounts:
            balance = float(account.balance or 0)
            account_type_str = account.account_type.value
            
            # Add to accounts_by_type
            if account_type_str not in accounts_by_type:
                accounts_by_type[account_type_str] = 0.0
            
            if account.account_type == AccountType.CURRENT:
                summary.current_balance += balance
                summary.total_assets += balance
                accounts_by_type[account_type_str] += balance
            elif account.account_type == AccountType.SAVINGS:
                summary.savings_balance += balance
                summary.total_assets += balance
                accounts_by_type[account_type_str] += balance
            elif account.account_type == AccountType.INVESTMENT:
                summary.investment_balance += balance
                summary.total_assets += balance
                accounts_by_type[account_type_str] += balance
            elif account.account_type == AccountType.CREDIT_CARD:
                # Credit card: negative balance means owed amount (liability)
                # positive balance means credit available (not counted)
                if balance < 0:
                    owed_amount = abs(balance)
                    summary.credit_card_balance += owed_amount
                    summary.total_liabilities += owed_amount
                    accounts_by_type[account_type_str] += owed_amount
            elif account.account_type == AccountType.LOAN:
                # For loans, use outstanding balance as liability (not the balance field)
                loan_outstanding = float(account.loan_outstanding or 0)
                summary.loan_outstanding += loan_outstanding
                summary.total_liabilities += loan_outstanding
                accounts_by_type[account_type_str] += loan_outstanding
                
                # Aggregate loan-specific metrics
                summary.total_loan_principal += float(account.loan_principal or 0)
                summary.total_emi_amount += float(account.emi_amount or 0)
                summary.total_interest_paid += float(account.total_interest_paid or 0)
                summary.total_principal_paid += float(account.total_principal_paid or 0)
            
            # Count connected accounts
            if account.is_connected:
                summary.connected_accounts += 1
        
        # Set accounts_by_type
        summary.accounts_by_type = accounts_by_type
        
        # Calculate net worth (assets - liabilities)
        summary.net_worth = summary.total_assets - summary.total_liabilities
        summary.last_updated = datetime.utcnow()
        
        return summary

# Made with Bob