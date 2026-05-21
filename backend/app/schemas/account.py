"""
Pydantic schemas for Financial Accounts
Request/Response models for account endpoints
"""
from datetime import datetime
from typing import Optional, Dict
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict, field_serializer

from app.models.account import AccountType, ConnectionStatus


# Base schema with common fields
class AccountBase(BaseModel):
    """Base schema for account data"""
    account_type: AccountType
    institution_name: str = Field(..., min_length=1, max_length=255)
    account_name: Optional[str] = Field(None, max_length=255)
    account_number_last4: Optional[str] = Field(None, min_length=4, max_length=4)
    balance: Optional[float] = None  # Can be negative for credit cards (owed amount)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    
    # Loan-specific fields (optional, only for loan accounts)
    loan_principal: Optional[float] = Field(None, ge=0, description="Original loan amount")
    loan_outstanding: Optional[float] = Field(None, ge=0, description="Current outstanding balance")
    interest_rate: Optional[float] = Field(None, ge=0, le=100, description="Annual interest rate percentage")
    emi_amount: Optional[float] = Field(None, ge=0, description="Monthly EMI amount")
    loan_tenure_months: Optional[int] = Field(None, ge=1, description="Total loan tenure in months")
    remaining_tenure_months: Optional[int] = Field(None, ge=0, description="Remaining months")
    loan_start_date: Optional[datetime] = Field(None, description="Loan start date")
    total_interest_paid: Optional[float] = Field(None, ge=0, description="Total interest paid so far")
    total_principal_paid: Optional[float] = Field(None, ge=0, description="Total principal paid so far")


# Schema for creating a new account
class AccountCreate(AccountBase):
    """Schema for creating a new financial account"""
    pass


# Schema for updating an account
class AccountUpdate(BaseModel):
    """Schema for updating an existing account"""
    account_name: Optional[str] = Field(None, max_length=255)
    balance: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None
    connection_status: Optional[ConnectionStatus] = None


# Schema for account response
class AccountResponse(AccountBase):
    """Schema for account response with all fields"""
    id: UUID
    user_id: UUID
    is_active: bool
    connection_status: ConnectionStatus
    last_synced: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    masked_account_number: Optional[str] = None
    is_connected: bool = False
    needs_sync: bool = True

    model_config = ConfigDict(from_attributes=True)


# Schema for account list response
class AccountListResponse(BaseModel):
    """Schema for paginated account list"""
    accounts: list[AccountResponse]
    total: int
    page: int = 1
    page_size: int = 50


# Schema for account summary
class AccountSummary(BaseModel):
    """Schema for financial summary across accounts"""
    total_assets: float = Field(default=0.0, description="Total assets (current + savings + investments)")
    total_liabilities: float = Field(default=0.0, description="Total liabilities (credit cards + loans)")
    net_worth: float = Field(default=0.0, description="Net worth (assets - liabilities)")
    
    # Breakdown by account type (Assets)
    current_balance: float = Field(default=0.0)
    savings_balance: float = Field(default=0.0)
    investment_balance: float = Field(default=0.0)
    
    # Breakdown by account type (Liabilities)
    credit_card_balance: float = Field(default=0.0, description="Total credit card debt")
    loan_outstanding: float = Field(default=0.0, description="Total outstanding loan balance")
    
    # Loan-specific summary
    total_loan_principal: float = Field(default=0.0, description="Total original loan amounts")
    total_emi_amount: float = Field(default=0.0, description="Total monthly EMI across all loans")
    total_interest_paid: float = Field(default=0.0, description="Total interest paid across all loans")
    total_principal_paid: float = Field(default=0.0, description="Total principal paid across all loans")
    
    # Detailed breakdown
    accounts_by_type: Dict[str, float] = Field(default_factory=dict)
    
    # Account counts
    total_accounts: int = 0
    active_accounts: int = 0
    connected_accounts: int = 0
    
    last_updated: datetime = Field(default_factory=datetime.utcnow)


# Schema for account sync request
class AccountSyncRequest(BaseModel):
    """Schema for triggering account synchronization"""
    force: bool = Field(default=False, description="Force sync even if recently synced")


# Schema for account sync response
class AccountSyncResponse(BaseModel):
    """Schema for account sync result"""
    account_id: UUID
    success: bool
    message: str
    last_synced: Optional[datetime] = None
    transactions_imported: int = 0

# Made with Bob