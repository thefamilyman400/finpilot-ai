"""
Transaction Model
Represents financial transactions for user accounts
"""
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy import String, Numeric, Boolean, DateTime, Date, Text, ARRAY, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import enum

from app.db.base import Base


class TransactionType(str, enum.Enum):
    """Types of transactions"""
    DEBIT = "debit"
    CREDIT = "credit"


class TransactionCategory(str, enum.Enum):
    """Common transaction categories"""
    # Income
    SALARY = "salary"
    FREELANCE = "freelance"
    INVESTMENT_INCOME = "investment_income"
    OTHER_INCOME = "other_income"
    
    # Housing
    RENT = "rent"
    MORTGAGE = "mortgage"
    UTILITIES = "utilities"
    HOME_MAINTENANCE = "home_maintenance"
    
    # Transportation
    GAS = "gas"
    PUBLIC_TRANSIT = "public_transit"
    CAR_PAYMENT = "car_payment"
    CAR_MAINTENANCE = "car_maintenance"
    PARKING = "parking"
    
    # Food
    GROCERIES = "groceries"
    RESTAURANTS = "restaurants"
    COFFEE = "coffee"
    
    # Shopping
    CLOTHING = "clothing"
    ELECTRONICS = "electronics"
    GENERAL_SHOPPING = "general_shopping"
    
    # Entertainment
    ENTERTAINMENT = "entertainment"
    SUBSCRIPTIONS = "subscriptions"
    HOBBIES = "hobbies"
    
    # Healthcare
    MEDICAL = "medical"
    PHARMACY = "pharmacy"
    INSURANCE = "insurance"
    
    # Financial
    SAVINGS = "savings"
    INVESTMENTS = "investments"
    LOAN_PAYMENT = "loan_payment"
    CREDIT_CARD_PAYMENT = "credit_card_payment"
    FEES = "fees"
    
    # Other
    EDUCATION = "education"
    GIFTS = "gifts"
    CHARITY = "charity"
    TAXES = "taxes"
    UNCATEGORIZED = "uncategorized"


class Transaction(Base):
    """
    Transaction Model
    Stores financial transactions for user accounts
    """
    __tablename__ = "transactions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    account_id: Mapped[UUID] = mapped_column(ForeignKey("financial_accounts.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    # Transaction details
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    transaction_type: Mapped[TransactionType] = mapped_column(
        SQLEnum(TransactionType, native_enum=False),
        nullable=False
    )
    
    # Categorization
    category: Mapped[Optional[TransactionCategory]] = mapped_column(
        SQLEnum(TransactionCategory, native_enum=False),
        index=True
    )
    merchant_name: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Additional metadata
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), default=list)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    account = relationship("FinancialAccount", back_populates="transactions")
    user = relationship("User", back_populates="transactions")

    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, date={self.transaction_date}, amount={self.amount}, type={self.transaction_type})>"

    @property
    def is_expense(self) -> bool:
        """Check if transaction is an expense (debit)"""
        return self.transaction_type == TransactionType.DEBIT

    @property
    def is_income(self) -> bool:
        """Check if transaction is income (credit)"""
        return self.transaction_type == TransactionType.CREDIT

    @property
    def formatted_amount(self) -> str:
        """Return formatted amount with currency symbol"""
        symbol = "-" if self.is_expense else "+"
        return f"{symbol}${abs(float(self.amount)):.2f}"

    @property
    def is_categorized(self) -> bool:
        """Check if transaction has been categorized"""
        return self.category is not None and self.category != TransactionCategory.UNCATEGORIZED

# Made with Bob