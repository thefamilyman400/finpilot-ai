"""
Document Parser Service
Extracts financial data from uploaded documents (bank statements, credit card statements, etc.)
and automatically creates accounts and transactions
"""
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from decimal import Decimal
import PyPDF2
from io import BytesIO

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.account import AccountType
from app.models.transaction import TransactionType, TransactionCategory
from app.services.account_service import AccountService
from app.services.transaction_service import TransactionService
from app.schemas.account import AccountCreate
from app.schemas.transaction import TransactionCreate


class DocumentParserService:
    """Service for parsing financial documents and extracting data"""
    
    # Common bank patterns for Indian banks
    BANK_PATTERNS = {
        'HDFC': r'HDFC\s*BANK',
        'ICICI': r'ICICI\s*BANK',
        'SBI': r'STATE\s*BANK\s*OF\s*INDIA|SBI',
        'AXIS': r'AXIS\s*BANK',
        'KOTAK': r'KOTAK\s*MAHINDRA\s*BANK',
        'YES': r'YES\s*BANK',
        'IDFC': r'IDFC\s*FIRST\s*BANK',
        'RBL': r'RBL\s*BANK',
    }
    
    # Transaction patterns
    TRANSACTION_PATTERNS = {
        'date': r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
        'amount': r'(?:Rs\.?|INR|₹)\s*([0-9,]+\.?\d*)',
        'debit': r'(?:debit|dr|withdrawal|paid)',
        'credit': r'(?:credit|cr|deposit|received)',
    }
    
    # Account number pattern
    ACCOUNT_NUMBER_PATTERN = r'(?:A/c|Account|A/C)\s*(?:No\.?|Number)?\s*:?\s*(\d{9,18})'
    
    @staticmethod
    async def parse_document(
        db: AsyncSession,
        user_id: str,
        file_content: bytes,
        file_name: str,
        file_type: str
    ) -> Dict[str, Any]:
        """
        Parse a financial document and extract data
        
        Args:
            db: Database session
            user_id: User ID
            file_content: File content as bytes
            file_name: Original file name
            file_type: MIME type
            
        Returns:
            Dictionary with parsed data and actions taken
        """
        result = {
            'file_name': file_name,
            'detected_bank': None,
            'detected_account_type': None,
            'account_number': None,
            'transactions_found': 0,
            'accounts_created': 0,
            'transactions_created': 0,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Extract text from document
            text = await DocumentParserService._extract_text(file_content, file_type)
            
            if not text:
                result['errors'].append('Could not extract text from document')
                return result
            
            # Detect bank
            bank_name = DocumentParserService._detect_bank(text)
            result['detected_bank'] = bank_name
            
            # Detect account type
            account_type = DocumentParserService._detect_account_type(text)
            result['detected_account_type'] = account_type
            
            # Extract account number
            account_number = DocumentParserService._extract_account_number(text)
            result['account_number'] = account_number
            
            # Extract transactions
            transactions = DocumentParserService._extract_transactions(text)
            result['transactions_found'] = len(transactions)
            
            # Create or find account
            account = None
            if bank_name and account_number:
                try:
                    account = await DocumentParserService._get_or_create_account(
                        db, user_id, bank_name, account_number, account_type
                    )
                    if account:
                        result['accounts_created'] = 1
                except ValueError as e:
                    # Credit card validation failed
                    result['errors'].append(str(e))
                    return result
            
            # Create transactions
            if account and transactions:
                created_count = await DocumentParserService._create_transactions(
                    db, user_id, account.id, transactions
                )
                result['transactions_created'] = created_count
            elif not account:
                result['warnings'].append('Could not create account - transactions not imported')
            
            return result
            
        except Exception as e:
            result['errors'].append(f'Error parsing document: {str(e)}')
            return result
    
    @staticmethod
    async def _extract_text(file_content: bytes, file_type: str) -> str:
        """Extract text from PDF or text file"""
        try:
            if 'pdf' in file_type.lower():
                # Extract from PDF
                pdf_file = BytesIO(file_content)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text = ''
                for page in pdf_reader.pages:
                    text += page.extract_text() + '\n'
                return text
            else:
                # Assume text file
                return file_content.decode('utf-8', errors='ignore')
        except Exception as e:
            print(f'Error extracting text: {str(e)}')
            return ''
    
    @staticmethod
    def _detect_bank(text: str) -> Optional[str]:
        """Detect bank name from document text"""
        text_upper = text.upper()
        for bank, pattern in DocumentParserService.BANK_PATTERNS.items():
            if re.search(pattern, text_upper, re.IGNORECASE):
                return bank
        return None
    
    @staticmethod
    def _detect_account_type(text: str) -> AccountType:
        """Detect account type from document text"""
        text_lower = text.lower()
        
        # Check for savings account first (more specific)
        if re.search(r'savings?\s+account|savings?\s+a/c', text_lower):
            return AccountType.SAVINGS
        # Check for current account
        elif re.search(r'current\s+account|current\s+a/c', text_lower):
            return AccountType.CURRENT
        # Check for credit card - must be very specific phrases to avoid false positives
        # Only match if "credit card" appears together or card-specific terms
        elif re.search(r'credit\s+card\s+(statement|account|number)|card\s+statement|credit\s+limit|total\s+amount\s+due|minimum\s+amount\s+due|payment\s+due\s+date', text_lower):
            return AccountType.CREDIT_CARD
        # Check for loan account
        elif re.search(r'loan\s+account|emi\s+amount|loan\s+principal|loan\s+outstanding', text_lower):
            return AccountType.LOAN
        # Check for general bank statement indicators (default to current)
        elif re.search(r'bank\s+statement|account\s+statement|transaction\s+history', text_lower):
            return AccountType.CURRENT
        else:
            return AccountType.CURRENT  # Default
    
    @staticmethod
    def _extract_account_number(text: str) -> Optional[str]:
        """Extract account number from text"""
        match = re.search(DocumentParserService.ACCOUNT_NUMBER_PATTERN, text, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
    
    @staticmethod
    def _extract_transactions(text: str) -> List[Dict[str, Any]]:
        """Extract transactions from document text"""
        transactions = []
        lines = text.split('\n')
        
        for line in lines:
            # Look for lines with dates and amounts
            date_match = re.search(DocumentParserService.TRANSACTION_PATTERNS['date'], line)
            amount_match = re.search(DocumentParserService.TRANSACTION_PATTERNS['amount'], line, re.IGNORECASE)
            
            if date_match and amount_match:
                date_str = date_match.group(1)
                amount_str = amount_match.group(1).replace(',', '')
                
                try:
                    # Parse date
                    transaction_date = DocumentParserService._parse_date(date_str)
                    
                    # Parse amount
                    amount = float(amount_str)
                    
                    # Determine transaction type
                    line_lower = line.lower()
                    is_debit = bool(re.search(DocumentParserService.TRANSACTION_PATTERNS['debit'], line_lower, re.IGNORECASE))
                    is_credit = bool(re.search(DocumentParserService.TRANSACTION_PATTERNS['credit'], line_lower, re.IGNORECASE))
                    
                    transaction_type = TransactionType.DEBIT if is_debit else TransactionType.CREDIT
                    
                    # Extract description (rest of the line)
                    description = line.strip()
                    
                    # Categorize transaction
                    category = DocumentParserService._categorize_transaction(description)
                    
                    transactions.append({
                        'date': transaction_date,
                        'amount': amount,
                        'type': transaction_type,
                        'description': description,
                        'category': category
                    })
                    
                except Exception as e:
                    print(f'Error parsing transaction line: {line}, Error: {str(e)}')
                    continue
        
        return transactions
    
    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        """Parse date string in various formats"""
        # Try different date formats
        formats = [
            '%d-%m-%Y', '%d/%m/%Y', '%d-%m-%y', '%d/%m/%y',
            '%Y-%m-%d', '%Y/%m/%d',
            '%d %b %Y', '%d %B %Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # Default to today if parsing fails
        return datetime.now()
    
    @staticmethod
    def _categorize_transaction(description: str) -> TransactionCategory:
        """Automatically categorize transaction based on description"""
        desc_lower = description.lower()
        
        # Food & Dining
        if any(word in desc_lower for word in ['restaurant', 'cafe', 'food', 'zomato', 'swiggy', 'uber eats']):
            return TransactionCategory.RESTAURANTS
        
        if any(word in desc_lower for word in ['grocery', 'supermarket', 'vegetables', 'fruits']):
            return TransactionCategory.GROCERIES
        
        # Shopping
        if any(word in desc_lower for word in ['amazon', 'flipkart', 'shopping', 'mall', 'store']):
            return TransactionCategory.GENERAL_SHOPPING
        
        if any(word in desc_lower for word in ['clothing', 'fashion', 'apparel']):
            return TransactionCategory.CLOTHING
        
        # Transportation
        if any(word in desc_lower for word in ['uber', 'ola', 'metro', 'bus', 'taxi']):
            return TransactionCategory.PUBLIC_TRANSIT
        
        if any(word in desc_lower for word in ['fuel', 'petrol', 'diesel', 'gas station']):
            return TransactionCategory.GAS
        
        # Bills & Utilities
        if any(word in desc_lower for word in ['electricity', 'water', 'internet', 'mobile', 'recharge']):
            return TransactionCategory.UTILITIES
        
        # Healthcare
        if any(word in desc_lower for word in ['hospital', 'doctor', 'medical', 'health']):
            return TransactionCategory.MEDICAL
        
        if any(word in desc_lower for word in ['pharmacy', 'medicine', 'drug']):
            return TransactionCategory.PHARMACY
        
        # Entertainment
        if any(word in desc_lower for word in ['movie', 'netflix', 'prime', 'spotify', 'game', 'subscription']):
            return TransactionCategory.ENTERTAINMENT
        
        # Salary/Income
        if any(word in desc_lower for word in ['salary', 'income', 'payment received']):
            return TransactionCategory.SALARY
        
        # Default
        return TransactionCategory.UNCATEGORIZED
    
    @staticmethod
    async def _get_or_create_account(
        db: AsyncSession,
        user_id: str,
        bank_name: str,
        account_number: str,
        account_type: AccountType
    ):
        """Get existing account or create new one"""
        from uuid import UUID
        from sqlalchemy import select
        from app.models.account import FinancialAccount
        
        # Check if account already exists
        result = await db.execute(
            select(FinancialAccount).where(
                FinancialAccount.user_id == UUID(user_id),
                FinancialAccount.account_number_last4 == account_number[-4:]
            )
        )
        existing_account = result.scalar_one_or_none()
        
        if existing_account:
            return existing_account
        
        # Create new account
        account_data = AccountCreate(
            account_type=account_type,
            institution_name=bank_name,
            account_name=f'{bank_name} {account_type.value.title()}',
            account_number_last4=account_number[-4:],
            balance=0.0,
            currency='INR',
            loan_principal=None,
            loan_outstanding=None,
            interest_rate=None,
            emi_amount=None,
            loan_tenure_months=None,
            remaining_tenure_months=None,
            loan_start_date=None,
            total_interest_paid=0,
            total_principal_paid=0
        )
        
        account = await AccountService.create_account(db, UUID(user_id), account_data)
        return account
    
    @staticmethod
    async def _create_transactions(
        db: AsyncSession,
        user_id: str,
        account_id,  # Can be UUID or str
        transactions: List[Dict[str, Any]]
    ) -> int:
        """Create transactions from parsed data"""
        from uuid import UUID
        created_count = 0
        
        # Convert account_id to UUID if it's not already
        if isinstance(account_id, str):
            account_id = UUID(account_id)
        
        for txn in transactions:
            try:
                transaction_data = TransactionCreate(
                    account_id=account_id,
                    transaction_date=txn['date'],
                    description=txn['description'],
                    amount=txn['amount'],
                    transaction_type=txn['type'],
                    category=txn['category'],
                    merchant_name=None  # Will be extracted in future enhancement
                )
                
                await TransactionService.create_transaction(db, UUID(user_id), transaction_data)
                created_count += 1
                
            except Exception as e:
                print(f'Error creating transaction: {str(e)}')
                continue
        
        return created_count


# Singleton instance
document_parser_service = DocumentParserService()

# Made with Bob