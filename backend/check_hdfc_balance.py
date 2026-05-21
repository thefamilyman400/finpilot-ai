"""
Check HDFC account balance and transaction totals
"""
import asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import select
from app.models.account import FinancialAccount
from app.models.transaction import Transaction

async def check_hdfc():
    async with AsyncSessionLocal() as db:
        # Find HDFC account
        result = await db.execute(
            select(FinancialAccount).where(
                FinancialAccount.institution_name.ilike('%hdfc%')
            )
        )
        account = result.scalar_one_or_none()
        
        if not account:
            print('No HDFC account found')
            return
        
        print(f'\n=== HDFC Account ===')
        print(f'Account ID: {account.id}')
        print(f'Account Type: {account.account_type}')
        print(f'Balance in DB: Rs.{account.balance:,.2f}')
        
        # Get all transactions
        tx_result = await db.execute(
            select(Transaction).where(
                Transaction.account_id == account.id
            ).order_by(Transaction.transaction_date)
        )
        transactions = tx_result.scalars().all()
        
        print(f'\n=== Transactions ===')
        print(f'Total Transactions: {len(transactions)}')
        
        # Calculate totals
        from app.models.transaction import TransactionType
        credits = sum(t.amount for t in transactions if t.transaction_type == TransactionType.CREDIT)
        debits = sum(t.amount for t in transactions if t.transaction_type == TransactionType.DEBIT)
        
        print(f'Total Credits: Rs.{credits:,.2f}')
        print(f'Total Debits: Rs.{debits:,.2f}')
        print(f'Calculated Balance (Credits - Debits): Rs.{credits - debits:,.2f}')
        print(f'\nDifference from DB Balance: Rs.{(credits - debits) - account.balance:,.2f}')
        
        # Show first and last few transactions
        print(f'\n=== First 5 Transactions ===')
        for t in transactions[:5]:
            print(f'{t.transaction_date} | {t.transaction_type:6} | Rs.{t.amount:>12,.2f} | {t.description[:50]}')
        
        print(f'\n=== Last 5 Transactions ===')
        for t in transactions[-5:]:
            print(f'{t.transaction_date} | {t.transaction_type:6} | Rs.{t.amount:>12,.2f} | {t.description[:50]}')

if __name__ == "__main__":
    asyncio.run(check_hdfc())

# Made with Bob
