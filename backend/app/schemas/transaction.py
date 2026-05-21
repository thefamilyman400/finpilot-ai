"""
Pydantic schemas for Transactions
Request/Response models for transaction endpoints
"""
from datetime import datetime, date
from typing import Optional, List, Any, Union
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.models.transaction import TransactionType, TransactionCategory


# Base schema with common fields
class TransactionBase(BaseModel):
    """Base schema for transaction data"""
    transaction_date: Union[date, datetime]
    description: Optional[str] = None
    amount: float
    transaction_type: TransactionType
    category: Optional[TransactionCategory] = None
    merchant_name: Optional[str] = Field(None, max_length=255)
    is_recurring: bool = False
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    
    @field_validator('transaction_date', mode='before')
    @classmethod
    def parse_date(cls, v):
        """Convert datetime to date if needed"""
        if isinstance(v, str):
            # Try parsing as datetime first, then as date
            try:
                dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
                return dt.date()
            except:
                return datetime.strptime(v, '%Y-%m-%d').date()
        elif isinstance(v, datetime):
            return v.date()
        return v


# Schema for creating a new transaction
class TransactionCreate(TransactionBase):
    """Schema for creating a new transaction"""
    account_id: UUID


# Schema for updating a transaction
class TransactionUpdate(BaseModel):
    """Schema for updating an existing transaction"""
    transaction_date: Optional[Union[date, datetime]] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    transaction_type: Optional[TransactionType] = None
    category: Optional[TransactionCategory] = None
    merchant_name: Optional[str] = Field(None, max_length=255)
    is_recurring: Optional[bool] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    
    @field_validator('transaction_date', mode='before')
    @classmethod
    def parse_date(cls, v):
        """Convert datetime to date if needed"""
        if v is None:
            return v
        if isinstance(v, str):
            try:
                dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
                return dt.date()
            except:
                return datetime.strptime(v, '%Y-%m-%d').date()
        elif isinstance(v, datetime):
            return v.date()
        return v


# Schema for transaction response
class TransactionResponse(TransactionBase):
    """Schema for transaction response with all fields"""
    id: UUID
    account_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    is_expense: bool = False
    is_income: bool = False
    formatted_amount: str = "$0.00"
    is_categorized: bool = False

    model_config = ConfigDict(from_attributes=True)


# Schema for transaction filters
class TransactionFilters(BaseModel):
    """Schema for filtering transactions"""
    account_id: Optional[UUID] = None
    transaction_type: Optional[TransactionType] = None
    category: Optional[TransactionCategory] = None
    merchant_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    is_recurring: Optional[bool] = None
    tags: Optional[List[str]] = None
    search: Optional[str] = Field(None, description="Search in description and merchant name")


# Schema for transaction list response
class TransactionListResponse(BaseModel):
    """Schema for paginated transaction list"""
    transactions: List[TransactionResponse]
    total: int
    page: int = 1
    page_size: int = 50
    total_income: float = Field(default=0.0)
    total_expenses: float = Field(default=0.0)
    net_amount: float = Field(default=0.0)


# Schema for bulk categorization
class BulkCategorizeRequest(BaseModel):
    """Schema for bulk categorizing transactions"""
    transaction_ids: List[UUID] = Field(..., min_length=1)
    category: TransactionCategory


# Schema for bulk categorization response
class BulkCategorizeResponse(BaseModel):
    """Schema for bulk categorization result"""
    success: bool
    updated_count: int
    failed_ids: List[UUID] = Field(default_factory=list)
    message: str


# Schema for transaction analytics
class TransactionAnalytics(BaseModel):
    """Schema for transaction analytics"""
    # Time period
    start_date: date
    end_date: date
    
    # Summary
    total_income: float = Field(default=0.0)
    total_expenses: float = Field(default=0.0)
    net_amount: float = Field(default=0.0)
    transaction_count: int = 0
    
    # Average values
    avg_transaction_amount: float = Field(default=0.0)
    avg_daily_spending: float = Field(default=0.0)
    
    # Category breakdown
    spending_by_category: dict[str, float] = Field(default_factory=dict)
    income_by_category: dict[str, float] = Field(default_factory=dict)
    
    # Top merchants
    top_merchants: List[dict[str, Any]] = Field(default_factory=list)
    
    # Trends
    daily_totals: List[dict[str, Any]] = Field(default_factory=list)
    monthly_totals: List[dict[str, Any]] = Field(default_factory=list)
    
    # Recurring transactions
    recurring_count: int = 0
    recurring_total: float = Field(default=0.0)


# Schema for category statistics
class CategoryStatistics(BaseModel):
    """Schema for category-wise statistics"""
    category: TransactionCategory
    total_amount: float
    transaction_count: int
    percentage_of_total: float = Field(ge=0, le=100)
    avg_transaction_amount: float


# Schema for spending insights
class SpendingInsights(BaseModel):
    """Schema for spending insights and patterns"""
    period: str  # "week", "month", "year"
    total_spending: float
    
    # Comparisons
    vs_previous_period: float
    vs_previous_period_percentage: float
    
    # Top categories
    top_spending_categories: List[CategoryStatistics]
    
    # Unusual spending
    unusual_transactions: List[TransactionResponse] = Field(default_factory=list)
    
    # Recommendations
    insights: List[str] = Field(default_factory=list)

# Made with Bob