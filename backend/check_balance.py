import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.account import FinancialAccount
from app.models.transaction import Transaction, TransactionType

async def check_balance():
    async with AsyncSessionLocal() as db:
        # Get HDFC account
        result = await db.execute(
            select(FinancialAccount).where(FinancialAccount.institution_name == 'HDFC')
        )
        account = result.scalar_one_or_none()
        
        if not account:
            print('No HDFC account found')
            return
        
        print(f'Account: {account.account_name}')
        print(f'Account Number: ****{account.account_number_last4}')
        print(f'Current Balance in DB: Rs.{account.balance:,.2f}')
        print(f'Account ID: {account.id}')
        
        # Get all transactions for this account
        txn_result = await db.execute(
            select(Transaction).where(Transaction.account_id == account.id)
        )
        transactions = txn_result.scalars().all()
        
        # Calculate totals
        total_credits = sum(t.amount for t in transactions if t.transaction_type == TransactionType.CREDIT)
        total_debits = sum(t.amount for t in transactions if t.transaction_type == TransactionType.DEBIT)
        calculated_balance = total_credits - total_debits
        
        print(f'\nTransaction Summary:')
        print(f'Total Credits: Rs.{total_credits:,.2f}')
        print(f'Total Debits: Rs.{total_debits:,.2f}')
        print(f'Transaction Count: {len(transactions)}')
        print(f'Calculated Balance (Credits - Debits): Rs.{calculated_balance:,.2f}')
        
        # Check if balance matches
        difference = account.balance - calculated_balance
        print(f'\nBalance Verification:')
        if abs(difference) < 0.01:
            print('Status: CORRECT - Balance matches!')
        else:
            print(f'Status: INCORRECT - Difference: Rs.{difference:,.2f}')
            print(f'DB Balance: Rs.{account.balance:,.2f}')
            print(f'Calculated: Rs.{calculated_balance:,.2f}')

if __name__ == '__main__':
    asyncio.run(check_balance())

# Made with Bob
