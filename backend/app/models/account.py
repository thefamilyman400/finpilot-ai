"""
Financial Account Model
Represents user's financial accounts (current, savings, credit cards, investments, loans)
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, Numeric, Boolean, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import enum

from app.db.base import Base


class AccountType(str, enum.Enum):
    """Types of financial accounts"""
    CURRENT = "current"
    SAVINGS = "savings"
    CREDIT_CARD = "credit_card"
    INVESTMENT = "investment"
    LOAN = "loan"
    OTHER = "other"


class ConnectionStatus(str, enum.Enum):
    """Account connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    MANUAL = "manual"


class FinancialAccount(Base):
    """
    Financial Account Model
    Stores information about user's financial accounts
    """
    __tablename__ = "financial_accounts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    # Account details
    account_type: Mapped[AccountType] = mapped_column(
        SQLEnum(AccountType, native_enum=False),
        nullable=False,
        index=True
    )
    institution_name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_name: Mapped[Optional[str]] = mapped_column(String(255))
    account_number_last4: Mapped[Optional[str]] = mapped_column(String(4))
    
    # Financial data
    balance: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    
    # Loan-specific fields
    loan_principal: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))  # Original loan amount
    loan_outstanding: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))  # Current outstanding balance
    interest_rate: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))  # Annual interest rate percentage
    emi_amount: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))  # Monthly EMI amount
    loan_tenure_months: Mapped[Optional[int]] = mapped_column()  # Total loan tenure in months
    remaining_tenure_months: Mapped[Optional[int]] = mapped_column()  # Remaining months
    loan_start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    total_interest_paid: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), default=0.0)
    total_principal_paid: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), default=0.0)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    connection_status: Mapped[ConnectionStatus] = mapped_column(
        SQLEnum(ConnectionStatus, native_enum=False),
        default=ConnectionStatus.MANUAL
    )
    
    # Sync information
    last_synced: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
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
    user = relationship("User", back_populates="financial_accounts")
    transactions = relationship(
        "Transaction",
        back_populates="account",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<FinancialAccount(id={self.id}, type={self.account_type}, institution={self.institution_name})>"

    @property
    def masked_account_number(self) -> Optional[str]:
        """Return masked account number"""
        if self.account_number_last4:
            return f"****{self.account_number_last4}"
        return None

    @property
    def is_connected(self) -> bool:
        """Check if account is connected to external service"""
        return self.connection_status == ConnectionStatus.CONNECTED

    @property
    def needs_sync(self) -> bool:
        """Check if account needs synchronization"""
        if not self.last_synced:
            return True
        # Consider account needs sync if not synced in last 24 hours
        time_since_sync = datetime.utcnow() - self.last_synced
        return time_since_sync.total_seconds() > 86400  # 24 hours

# Made with Bob