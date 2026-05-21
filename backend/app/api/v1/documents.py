"""
Documents API endpoints
Handles document upload, processing, analysis, and retrieval
"""
from typing import List, Optional, Dict
from uuid import UUID
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
import os

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.document import DocumentType, ProcessingStatus
from app.schemas.document import (
    DocumentResponse,
    DocumentUpdate,
    DocumentUploadResponse,
    ProcessDocumentRequest,
    ProcessDocumentResponse,
    DocumentAnalysisRequest,
    DocumentSearchRequest,
    DocumentListResponse,
)
from app.services.document_service import document_service


router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    document_type: DocumentType = Form(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a new document
    
    - **file**: Document file to upload
    - **document_type**: Type of document
    - **title**: Optional document title
    - **description**: Optional description
    """
    try:
        document = await document_service.create_document(
            db=db,
            user_id=current_user.id,
            file=file,
            document_type=document_type,
            title=title,
            description=description,
        )
        
        return DocumentUploadResponse(
            id=document.id,
            filename=document.filename,
            file_size=document.file_size,
            file_type=document.file_type,
            document_type=document.document_type,
            status=document.status,
            message="Document uploaded successfully",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific document by ID"""
    document = await document_service.get_document(db, document_id, current_user.id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    document_type: Optional[DocumentType] = Query(None),
    status_filter: Optional[ProcessingStatus] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List user's documents with optional filters
    
    - **document_type**: Filter by document type
    - **status**: Filter by processing status
    - **skip**: Number of documents to skip
    - **limit**: Maximum number of documents to return
    """
    documents = await document_service.list_documents(
        db=db,
        user_id=current_user.id,
        document_type=document_type,
        status=status_filter,
        skip=skip,
        limit=limit,
    )
    return documents


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    update_data: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update document metadata"""
    document = await document_service.update_document(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
        update_data=update_data,
    )
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a document"""
    success = await document_service.delete_document(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return None


@router.get("/{document_id}/download")
async def download_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download a document file"""
    document = await document_service.get_document(db, document_id, current_user.id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if file exists
    if not os.path.exists(document.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found on server"
        )
    
    return FileResponse(
        path=document.file_path,
        filename=document.filename,
        media_type=document.file_type
    )


@router.post("/{document_id}/extract-text", response_model=ProcessDocumentResponse)
async def extract_text(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Extract text from a document
    
    Supports:
    - PDF files
    - DOCX files
    - Images (with OCR)
    - CSV files
    """
    try:
        extracted_text = await document_service.extract_text(
            db=db,
            document_id=document_id,
            user_id=current_user.id,
        )
        
        if extracted_text is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return ProcessDocumentResponse(
            id=document_id,
            status=ProcessingStatus.COMPLETED,
            message="Text extraction completed successfully",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text extraction failed: {str(e)}"
        )


@router.post("/{document_id}/analyze")
async def analyze_document(
    document_id: UUID,
    analysis_request: Optional[DocumentAnalysisRequest] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Analyze document with AI
    
    Provides:
    - Document summary
    - Key findings extraction
    - Entity recognition
    - Category classification
    - Confidence scoring
    """
    try:
        # Use default analysis request if none provided
        if analysis_request is None:
            analysis_request = DocumentAnalysisRequest()
        
        analysis = await document_service.analyze_document(
            db=db,
            document_id=document_id,
            user_id=current_user.id,
            analysis_request=analysis_request,
        )
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document analysis failed: {str(e)}"
        )


@router.post("/search", response_model=List[DocumentResponse])
async def search_documents(
    search_request: DocumentSearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Search documents by content or metadata
    
    Search criteria:
    - Text content (title, description, extracted text)
    - Document types
    - Tags
    - Date range
    """
    documents = await document_service.search_documents(
        db=db,
        user_id=current_user.id,
        search_request=search_request,
    )
    return documents


class TagsRequest(BaseModel):
    """Request model for adding tags"""
    tags: List[str]

@router.post("/{document_id}/tags", response_model=DocumentResponse)
async def add_tags(
    document_id: UUID,
    tag_data: TagsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add tags to a document"""
    tags = tag_data.tags
    document = await document_service.add_tags(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
        tags=tags,
    )
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document


@router.delete("/{document_id}/tags", response_model=DocumentResponse)
async def remove_tags(
    document_id: UUID,
    tags: List[str],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove tags from a document"""
    document = await document_service.remove_tags(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
        tags=tags,
    )
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document


# Made with Bob