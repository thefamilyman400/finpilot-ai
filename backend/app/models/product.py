"""
Product Models for Banking/Insurance Portal
Stores product information, policies, and documents
"""
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.db.base import Base


class Product(Base):
    """Model for banking and insurance products"""
    
    __tablename__ = "products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Product details
    product_type = Column(String(50), nullable=False, index=True)  # 'savings', 'insurance', 'loan', 'credit_card'
    product_name = Column(String(255), nullable=False)
    product_code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Features and criteria (stored as JSON for flexibility)
    features = Column(JSONB, nullable=True)  # List of product features
    eligibility_criteria = Column(JSONB, nullable=True)  # Eligibility requirements
    terms_and_conditions = Column(Text, nullable=True)
    
    # Financial details
    interest_rate = Column(Numeric(5, 2), nullable=True)  # e.g., 5.25%
    min_amount = Column(Numeric(15, 2), nullable=True)
    max_amount = Column(Numeric(15, 2), nullable=True)
    fees = Column(JSONB, nullable=True)  # Various fees as JSON
    
    # Status and metadata
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    display_order = Column(Integer, default=0)  # For sorting in UI
    product_metadata = Column(JSONB, nullable=True)  # Additional metadata
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    documents = relationship("ProductDocument", back_populates="product", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Product(id={self.id}, name={self.product_name}, type={self.product_type})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "product_type": self.product_type,
            "product_name": self.product_name,
            "product_code": self.product_code,
            "description": self.description,
            "features": self.features,
            "eligibility_criteria": self.eligibility_criteria,
            "interest_rate": float(self.interest_rate) if self.interest_rate else None,
            "min_amount": float(self.min_amount) if self.min_amount else None,
            "max_amount": float(self.max_amount) if self.max_amount else None,
            "fees": self.fees,
            "is_active": self.is_active,
            "product_metadata": self.product_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class ProductDocument(Base):
    """Model for product-related documents"""
    
    __tablename__ = "product_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Document details
    document_type = Column(String(50), nullable=False)  # 'policy', 'terms', 'brochure', 'faq'
    document_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)
    
    # Vector DB reference
    vector_id = Column(String(255), nullable=True)  # Reference to vector database entry
    content_hash = Column(String(64), nullable=True)  # SHA-256 hash for change detection
    
    # Metadata
    file_size = Column(Integer, nullable=True)  # Size in bytes
    mime_type = Column(String(100), nullable=True)
    is_indexed = Column(Boolean, default=False)  # Whether indexed in vector DB
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="documents")
    
    def __repr__(self):
        return f"<ProductDocument(id={self.id}, type={self.document_type}, product_id={self.product_id})>"


class PolicyDocument(Base):
    """Model for general policy documents (not product-specific)"""
    
    __tablename__ = "policy_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Document details
    document_name = Column(String(255), nullable=False)
    document_type = Column(String(50), nullable=False)  # 'regulatory', 'compliance', 'general_policy'
    category = Column(String(100), nullable=True)  # Additional categorization
    description = Column(Text, nullable=True)
    
    # File information
    file_path = Column(String(500), nullable=True)
    vector_id = Column(String(255), nullable=True)
    content_hash = Column(String(64), nullable=True)
    
    # Metadata
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    is_indexed = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Version control
    version = Column(String(20), nullable=True)
    effective_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<PolicyDocument(id={self.id}, name={self.document_name}, type={self.document_type})>"


# Made with Bob - Compliance-First AI Assistant