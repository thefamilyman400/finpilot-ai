"""
Document model for document intelligence and processing
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from app.db.base import Base


class DocumentType(str, enum.Enum):
    """Document type enumeration"""
    BANK_STATEMENT = "bank_statement"
    RECEIPT = "receipt"
    INVOICE = "invoice"
    TAX_FORM = "tax_form"
    PAYSLIP = "payslip"
    INSURANCE = "insurance"
    INVESTMENT = "investment"
    LOAN = "loan"
    CONTRACT = "contract"
    OTHER = "other"


class ProcessingStatus(str, enum.Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class Document(Base):
    """
    Document model for storing uploaded financial documents
    
    Attributes:
        id: Unique document identifier (UUID)
        user_id: Foreign key to user
        filename: Original filename
        file_path: Storage path
        file_size: File size in bytes
        file_type: MIME type
        document_type: Type of financial document
        status: Processing status
        extracted_text: Extracted text content
        extracted_data: Structured data extracted from document
        ai_analysis: AI-generated analysis and insights
        confidence_score: Confidence in extraction accuracy (0-1)
        page_count: Number of pages (for PDFs)
        language: Detected language
        tags: User-defined tags
        is_sensitive: Whether document contains sensitive data
        processed_at: When processing completed
        expires_at: Document expiration date
        created_at: Upload timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "documents"
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # File information
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    file_type = Column(String(100), nullable=False)  # MIME type
    
    # Document classification
    document_type = Column(SQLEnum(DocumentType), nullable=False, default=DocumentType.OTHER, index=True)
    
    # Processing status
    status = Column(SQLEnum(ProcessingStatus), nullable=False, default=ProcessingStatus.PENDING, index=True)
    
    # Extracted content
    extracted_text = Column(Text, nullable=True)
    extracted_data = Column(JSON, nullable=True)  # Structured data (amounts, dates, entities)
    ai_analysis = Column(JSON, nullable=True)  # AI-generated insights
    
    # Metadata
    confidence_score = Column(Integer, nullable=True)  # 0-100
    page_count = Column(Integer, nullable=True)
    language = Column(String(10), nullable=True, default="en")
    tags = Column(JSON, nullable=True)  # User-defined tags
    
    # Security and privacy
    is_sensitive = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    processed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="documents")
    
    @property
    def file_size_mb(self) -> float:
        """Get file size in megabytes"""
        return round(self.file_size / (1024 * 1024), 2)
    
    @property
    def is_processed(self) -> bool:
        """Check if document has been processed"""
        return self.status == ProcessingStatus.COMPLETED
    
    @property
    def is_pending(self) -> bool:
        """Check if document is pending processing"""
        return self.status == ProcessingStatus.PENDING
    
    @property
    def is_failed(self) -> bool:
        """Check if document processing failed"""
        return self.status == ProcessingStatus.FAILED
    
    @property
    def has_extracted_data(self) -> bool:
        """Check if document has extracted data"""
        return self.extracted_data is not None and len(self.extracted_data) > 0
    
    @property
    def has_ai_analysis(self) -> bool:
        """Check if document has AI analysis"""
        return self.ai_analysis is not None and len(self.ai_analysis) > 0
    
    @property
    def is_expired(self) -> bool:
        """Check if document has expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def processing_time_seconds(self) -> int:
        """Calculate processing time in seconds"""
        if self.processed_at and self.created_at:
            return int((self.processed_at - self.created_at).total_seconds())
        return 0
    
    def mark_as_processing(self):
        """Mark document as being processed"""
        self.status = ProcessingStatus.PROCESSING
        self.updated_at = datetime.utcnow()
    
    def mark_as_completed(self, extracted_text: str = None, extracted_data: dict = None, 
                         ai_analysis: dict = None, confidence_score: int = None):
        """Mark document as processed successfully"""
        self.status = ProcessingStatus.COMPLETED
        self.processed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        if extracted_text:
            self.extracted_text = extracted_text
        if extracted_data:
            self.extracted_data = extracted_data
        if ai_analysis:
            self.ai_analysis = ai_analysis
        if confidence_score is not None:
            self.confidence_score = confidence_score
    
    def mark_as_failed(self, error_message: str = None):
        """Mark document processing as failed"""
        self.status = ProcessingStatus.FAILED
        self.updated_at = datetime.utcnow()
        
        if error_message:
            if self.ai_analysis is None:
                self.ai_analysis = {}
            self.ai_analysis["error"] = error_message
    
    def archive(self):
        """Archive the document"""
        self.status = ProcessingStatus.ARCHIVED
        self.updated_at = datetime.utcnow()
    
    def add_tag(self, tag: str):
        """Add a tag to the document"""
        if self.tags is None:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()
    
    def remove_tag(self, tag: str):
        """Remove a tag from the document"""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename}, type={self.document_type}, status={self.status})>"


# Made with Bob