"""
Document Parser API Endpoints
Upload and parse financial documents to automatically extract data
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.services.document_parser_service import document_parser_service


router = APIRouter(tags=["Document Parser"])


@router.post(
    "",
    summary="Parse financial document and extract data",
    description="""
    Upload a financial document (bank statement, credit card statement, etc.) 
    and automatically extract:
    - Bank/Institution name
    - Account details
    - Transactions
    
    The system will:
    1. Detect the bank and account type
    2. Create the account if it doesn't exist
    3. Import all transactions found in the document
    
    Supported formats: PDF, TXT
    Supported banks: HDFC, ICICI, SBI, AXIS, KOTAK, YES, IDFC, RBL
    """
)
async def parse_document(
    file: UploadFile = File(..., description="Financial document to parse (PDF or TXT)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Parse a financial document and automatically create accounts and transactions.
    
    Returns:
    - detected_bank: Name of the bank detected
    - detected_account_type: Type of account (current, savings, credit_card, loan)
    - account_number: Last 4 digits of account number
    - transactions_found: Number of transactions detected in document
    - accounts_created: Number of new accounts created (0 or 1)
    - transactions_created: Number of transactions successfully imported
    - errors: List of any errors encountered
    - warnings: List of warnings
    """
    # Validate file type
    if not file.content_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not determine file type"
        )
    
    allowed_types = ['application/pdf', 'text/plain', 'application/octet-stream']
    filename = file.filename or "unknown.pdf"
    if file.content_type not in allowed_types and not filename.endswith(('.pdf', '.txt')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and TXT files are supported"
        )
    
    # Read file content
    try:
        file_content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading file: {str(e)}"
        )
    
    # Parse document
    try:
        result = await document_parser_service.parse_document(
            db=db,
            user_id=str(current_user.id),
            file_content=file_content,
            file_name=filename,
            file_type=file.content_type or "application/pdf"
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing document: {str(e)}"
        )


# Made with Bob