"""
User model for authentication and user management
"""
from sqlalchemy import Boolean, Column, String, DateTime, JSON
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    """
    User model for storing user account information
    
    Attributes:
        id: Unique user identifier (UUID)
        email: User's email address (unique)
        hashed_password: Bcrypt hashed password
        full_name: User's full name
        phone_number: User's phone number
        is_active: Whether the user account is active
        is_verified: Whether the user's email is verified
        last_login: Timestamp of last login
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "users"
    
    # Authentication fields
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile fields
    full_name = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=True)
    
    # User preferences (stored as JSON)
    preferences = Column(JSON, nullable=True, default={})
    
    # Status fields
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    financial_accounts = relationship("FinancialAccount", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    support_tickets = relationship("SupportTicket", back_populates="user", foreign_keys="[SupportTicket.user_id]", cascade="all, delete-orphan")
    simulations = relationship("FinancialSimulation", back_populates="user", cascade="all, delete-orphan")
    workflows = relationship("AutonomousWorkflow", back_populates="user", cascade="all, delete-orphan")
    # preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"

# Made with Bob
