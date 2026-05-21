"""
Document Service
Handles document upload, processing, text extraction, and AI analysis
"""
import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, HTTPException

from app.models.document import Document, DocumentType, ProcessingStatus
from app.schemas.document import (
    DocumentUpdate,
    DocumentAnalysisRequest,
    DocumentSearchRequest,
)
from config import settings


class DocumentService:
    """Service for document management and processing"""
    
    def __init__(self):
        self.upload_dir = Path(settings.DOCUMENT_UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Allowed file extensions - all types support all common formats
        common_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.csv', '.xls', '.xlsx', '.txt', '.docx', '.doc']
        self.allowed_extensions = {
            DocumentType.BANK_STATEMENT: common_extensions,
            DocumentType.TAX_FORM: common_extensions,
            DocumentType.INVOICE: common_extensions,
            DocumentType.RECEIPT: common_extensions,
            DocumentType.CONTRACT: common_extensions,
            DocumentType.INSURANCE: common_extensions,
            DocumentType.INVESTMENT: common_extensions,
            DocumentType.LOAN: common_extensions,
            DocumentType.PAYSLIP: common_extensions,
            DocumentType.OTHER: common_extensions,
        }
    
    async def create_document(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        file: UploadFile,
        document_type: DocumentType,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Document:
        """
        Upload and create a new document
        
        Args:
            db: Database session
            user_id: User ID
            file: Uploaded file
            document_type: Type of document
            title: Optional document title
            description: Optional description
            
        Returns:
            Created document
        """
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.allowed_extensions.get(document_type, []):
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not allowed for {document_type}"
            )
        
        # Generate unique filename
        file_id = uuid.uuid4()
        filename = f"{file_id}{file_ext}"
        file_path = self.upload_dir / str(user_id) / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save file
        try:
            content = await file.read()
            file_size = len(content)
            
            # Check file size limit (50MB)
            if file_size > settings.MAX_DOCUMENT_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File size exceeds maximum allowed size of {settings.MAX_DOCUMENT_SIZE / 1024 / 1024}MB"
                )
            
            with open(file_path, 'wb') as f:
                f.write(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        
        # Create document record
        document = Document(
            user_id=user_id,
            filename=file.filename,
            file_path=str(file_path),
            file_size=file_size,
            file_type=file.content_type or "application/octet-stream",
            document_type=document_type,
            status=ProcessingStatus.PENDING,
        )
        
        db.add(document)
        await db.commit()
        await db.refresh(document)
        
        return document
    
    async def get_document(
        self,
        db: AsyncSession,
        document_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Optional[Document]:
        """Get a document by ID"""
        result = await db.execute(
            select(Document).where(
                and_(
                    Document.id == document_id,
                    Document.user_id == user_id,
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def list_documents(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        document_type: Optional[DocumentType] = None,
        status: Optional[ProcessingStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Document]:
        """List user's documents with optional filters"""
        query = select(Document).where(Document.user_id == user_id)
        
        if document_type:
            query = query.where(Document.document_type == document_type)
        
        if status:
            query = query.where(Document.status == status)
        
        query = query.order_by(Document.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def update_document(
        self,
        db: AsyncSession,
        document_id: uuid.UUID,
        user_id: uuid.UUID,
        update_data: DocumentUpdate,
    ) -> Optional[Document]:
        """Update document metadata"""
        document = await self.get_document(db, document_id, user_id)
        if not document:
            return None
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(document, field, value)
        
        await db.commit()
        await db.refresh(document)
        return document
    
    async def delete_document(
        self,
        db: AsyncSession,
        document_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """Delete a document and its file"""
        document = await self.get_document(db, document_id, user_id)
        if not document:
            return False
        
        # Delete file
        try:
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
        except Exception as e:
            print(f"Warning: Failed to delete file {document.file_path}: {e}")
        
        # Delete database record
        await db.delete(document)
        await db.commit()
        return True
    
    async def extract_text(
        self,
        db: AsyncSession,
        document_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Optional[str]:
        """
        Extract text from document
        This is a placeholder - actual implementation would use:
        - PyPDF2 for PDFs
        - python-docx for DOCX
        - pytesseract for images
        """
        document = await self.get_document(db, document_id, user_id)
        if not document:
            return None
        
        # Update status
        document.status = ProcessingStatus.PROCESSING
        await db.commit()
        
        try:
            file_ext = Path(document.file_path).suffix.lower()
            extracted_text = ""
            
            if file_ext == '.pdf':
                # TODO: Implement PDF text extraction with PyPDF2
                extracted_text = f"[PDF text extraction not yet implemented for {document.filename}]"
            
            elif file_ext == '.docx':
                # TODO: Implement DOCX text extraction with python-docx
                extracted_text = f"[DOCX text extraction not yet implemented for {document.filename}]"
            
            elif file_ext in ['.jpg', '.jpeg', '.png']:
                # TODO: Implement OCR with pytesseract
                extracted_text = f"[Image OCR not yet implemented for {document.filename}]"
            
            elif file_ext == '.csv':
                # TODO: Implement CSV parsing
                extracted_text = f"[CSV parsing not yet implemented for {document.filename}]"
            
            else:
                extracted_text = f"[Unsupported file type: {file_ext}]"
            
            # Update document
            document.extracted_text = extracted_text
            document.status = ProcessingStatus.COMPLETED
            document.processed_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(document)
            
            return extracted_text
            
        except Exception as e:
            document.status = ProcessingStatus.FAILED
            document.ai_analysis = {"error": str(e)}
            await db.commit()
            raise HTTPException(status_code=500, detail=f"Text extraction failed: {str(e)}")
    
    async def analyze_document(
        self,
        db: AsyncSession,
        document_id: uuid.UUID,
        user_id: uuid.UUID,
        analysis_request: DocumentAnalysisRequest,
    ) -> Dict[str, Any]:
        """
        Analyze document with AI
        This is a placeholder - actual implementation would use OpenAI API
        """
        document = await self.get_document(db, document_id, user_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Ensure text is extracted
        if not document.extracted_text:
            await self.extract_text(db, document_id, user_id)
            await db.refresh(document)
        
        # TODO: Implement AI analysis with OpenAI
        # For now, return placeholder analysis
        analysis = {
            "document_id": str(document_id),
            "document_type": document.document_type,
            "analysis_type": analysis_request.analysis_type,
            "summary": f"AI analysis placeholder for {document.filename}",
            "key_findings": [
                "This is a placeholder analysis",
                "Actual AI analysis will be implemented with OpenAI API",
            ],
            "confidence_score": 0.0,
            "entities": [],
            "categories": [],
        }
        
        # Update document with analysis
        document.ai_analysis = analysis
        document.confidence_score = 0.0
        await db.commit()
        
        return analysis
    
    async def search_documents(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        search_request: DocumentSearchRequest,
    ) -> List[Document]:
        """Search documents by text content or metadata"""
        query = select(Document).where(Document.user_id == user_id)
        
        if search_request.query:
            # Search in filename and extracted text
            search_term = f"%{search_request.query}%"
            query = query.where(
                or_(
                    Document.filename.ilike(search_term),
                    Document.extracted_text.ilike(search_term),
                )
            )
        
        if search_request.document_types:
            query = query.where(Document.document_type.in_(search_request.document_types))
        
        if search_request.tags:
            # Search for documents with any of the specified tags
            for tag in search_request.tags:
                query = query.where(Document.tags.contains([tag]))
        
        if search_request.date_from:
            query = query.where(Document.created_at >= search_request.date_from)
        
        if search_request.date_to:
            query = query.where(Document.created_at <= search_request.date_to)
        
        query = query.order_by(Document.created_at.desc())
        query = query.offset(search_request.skip).limit(search_request.limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def add_tags(
        self,
        db: AsyncSession,
        document_id: uuid.UUID,
        user_id: uuid.UUID,
        tags: List[str],
    ) -> Optional[Document]:
        """Add tags to a document"""
        document = await self.get_document(db, document_id, user_id)
        if not document:
            return None
        
        # Merge with existing tags
        existing_tags = set(document.tags or [])
        new_tags = existing_tags.union(set(tags))
        document.tags = list(new_tags)
        
        await db.commit()
        await db.refresh(document)
        return document
    
    async def remove_tags(
        self,
        db: AsyncSession,
        document_id: uuid.UUID,
        user_id: uuid.UUID,
        tags: List[str],
    ) -> Optional[Document]:
        """Remove tags from a document"""
        document = await self.get_document(db, document_id, user_id)
        if not document:
            return None
        
        # Remove specified tags
        existing_tags = set(document.tags or [])
        remaining_tags = existing_tags - set(tags)
        document.tags = list(remaining_tags)
        
        await db.commit()
        await db.refresh(document)
        return document


# Singleton instance
document_service = DocumentService()

# Made with Bob
