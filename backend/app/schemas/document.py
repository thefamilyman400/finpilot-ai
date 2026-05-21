"""
Pydantic schemas for document management and processing
"""
from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import UUID


class DocumentTypeEnum(str, Enum):
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


class ProcessingStatusEnum(str, Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


# Base schemas
class DocumentBase(BaseModel):
    """Base document schema"""
    document_type: DocumentTypeEnum = Field(default=DocumentTypeEnum.OTHER)
    tags: Optional[List[str]] = Field(default=None)
    is_sensitive: bool = Field(default=True)
    expires_at: Optional[datetime] = Field(default=None)


class DocumentCreate(DocumentBase):
    """Schema for creating a document (used after upload)"""
    filename: str = Field(..., min_length=1, max_length=255)
    file_path: str = Field(..., min_length=1, max_length=500)
    file_size: int = Field(..., gt=0)
    file_type: str = Field(..., min_length=1, max_length=100)
    page_count: Optional[int] = Field(default=None, ge=1)


class DocumentUpdate(BaseModel):
    """Schema for updating document metadata"""
    document_type: Optional[DocumentTypeEnum] = None
    tags: Optional[List[str]] = None
    is_sensitive: Optional[bool] = None
    expires_at: Optional[datetime] = None


class DocumentResponse(DocumentBase):
    """Schema for document response"""
    id: UUID
    user_id: UUID
    filename: str
    file_path: str
    file_size: int
    file_type: str
    status: ProcessingStatusEnum
    extracted_text: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    confidence_score: Optional[int] = None
    page_count: Optional[int] = None
    language: Optional[str] = None
    processed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Computed properties
    file_size_mb: Optional[float] = None
    is_processed: Optional[bool] = None
    is_pending: Optional[bool] = None
    is_failed: Optional[bool] = None
    has_extracted_data: Optional[bool] = None
    has_ai_analysis: Optional[bool] = None
    is_expired: Optional[bool] = None
    processing_time_seconds: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentListResponse(BaseModel):
    """Schema for paginated document list"""
    documents: List[DocumentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class DocumentSummary(BaseModel):
    """Schema for document statistics summary"""
    total_documents: int
    pending_documents: int
    processing_documents: int
    completed_documents: int
    failed_documents: int
    total_size_mb: float
    documents_by_type: Dict[str, int]
    recent_uploads: List[DocumentResponse]


# Upload schemas
class DocumentUploadResponse(BaseModel):
    """Schema for document upload response"""
    id: UUID
    filename: str
    file_size: int
    file_type: str
    document_type: DocumentTypeEnum
    status: ProcessingStatusEnum
    message: str = "Document uploaded successfully"


# Processing schemas
class ProcessDocumentRequest(BaseModel):
    """Schema for triggering document processing"""
    extract_text: bool = Field(default=True)
    extract_data: bool = Field(default=True)
    ai_analysis: bool = Field(default=True)
    language: Optional[str] = Field(default="en")


class ProcessDocumentResponse(BaseModel):
    """Schema for document processing response"""
    id: UUID
    status: ProcessingStatusEnum
    message: str
    task_id: Optional[str] = None  # Celery task ID


class DocumentAnalysisResult(BaseModel):
    """Schema for document analysis results"""
    document_id: str
    extracted_text: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    confidence_score: Optional[int] = None
    processing_time_seconds: int
    status: ProcessingStatusEnum


# Filter schemas
class DocumentFilters(BaseModel):
    """Schema for filtering documents"""
    document_type: Optional[DocumentTypeEnum] = None
    status: Optional[ProcessingStatusEnum] = None
    is_sensitive: Optional[bool] = None
    tags: Optional[List[str]] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    search_text: Optional[str] = None


# Batch operations
class BatchProcessRequest(BaseModel):
    """Schema for batch processing documents"""
    document_ids: List[str] = Field(..., min_length=1, max_length=50)
    
    @validator('document_ids')
    def validate_document_ids(cls, v):
        if len(v) < 1:
            raise ValueError('At least one document ID is required')
        if len(v) > 50:
            raise ValueError('Maximum 50 documents can be processed at once')
        return v
    extract_text: bool = Field(default=True)
    extract_data: bool = Field(default=True)
    ai_analysis: bool = Field(default=True)


class BatchProcessResponse(BaseModel):
    """Schema for batch processing response"""
    total_documents: int
    queued_documents: int
    failed_documents: int
    task_ids: List[str]
    message: str


# Download schema
class DocumentDownloadResponse(BaseModel):
    """Schema for document download information"""
    id: str
    filename: str
    file_path: str
    file_size: int
    file_type: str
    download_url: Optional[str] = None

# Analysis schemas
class DocumentAnalysisRequest(BaseModel):
    """Schema for requesting document analysis"""
    analysis_type: str = Field(default="general", description="Type of analysis: general, financial, legal, etc.")
    include_entities: bool = Field(default=True)
    include_summary: bool = Field(default=True)
    include_categories: bool = Field(default=True)


# Search schemas
class DocumentSearchRequest(BaseModel):
    """Schema for searching documents"""
    query: Optional[str] = Field(default=None, description="Search query for text content")
    document_types: Optional[List[DocumentTypeEnum]] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)
    date_from: Optional[datetime] = Field(default=None)
    date_to: Optional[datetime] = Field(default=None)
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=100)



# Made with Bob