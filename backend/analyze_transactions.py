"""
Detailed transaction analysis for HDFC account
"""
import asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import select
from app.models.account import FinancialAccount
from app.models.transaction import Transaction, TransactionType
from decimal import Decimal

async def analyze():
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
        
        # Get all transactions
        tx_result = await db.execute(
            select(Transaction).where(
                Transaction.account_id == account.id
            ).order_by(Transaction.transaction_date, Transaction.description)
        )
        transactions = tx_result.scalars().all()
        
        print(f'\n=== HDFC Transaction Analysis ===')
        print(f'Total Transactions in DB: {len(transactions)}')
        
        # Group by month
        from collections import defaultdict
        by_month = defaultdict(lambda: {'credits': Decimal('0'), 'debits': Decimal('0'), 'count': 0})
        
        for t in transactions:
            month_key = t.transaction_date.strftime('%Y-%m')
            by_month[month_key]['count'] += 1
            if t.transaction_type == TransactionType.CREDIT:
                by_month[month_key]['credits'] += Decimal(str(t.amount))
            else:
                by_month[month_key]['debits'] += Decimal(str(t.amount))
        
        print(f'\n=== Monthly Breakdown ===')
        total_credits = Decimal('0')
        total_debits = Decimal('0')
        
        for month in sorted(by_month.keys()):
            data = by_month[month]
            print(f'{month}: {data["count"]:3} txns | Credits: Rs.{data["credits"]:>12,.2f} | Debits: Rs.{data["debits"]:>12,.2f}')
            total_credits += data['credits']
            total_debits += data['debits']
        
        print(f'\n=== Totals ===')
        print(f'Total Credits:  Rs.{total_credits:>12,.2f}')
        print(f'Total Debits:   Rs.{total_debits:>12,.2f}')
        print(f'Net Balance:    Rs.{total_credits - total_debits:>12,.2f}')
        
        print(f'\n=== Expected vs Actual ===')
        expected_credits = Decimal('324936.00')
        expected_debits = Decimal('198042.99')
        expected_balance = Decimal('126893.01')
        
        print(f'Expected Credits:  Rs.{expected_credits:>12,.2f}')
        print(f'Actual Credits:    Rs.{total_credits:>12,.2f}')
        print(f'Difference:        Rs.{expected_credits - total_credits:>12,.2f}')
        print()
        print(f'Expected Debits:   Rs.{expected_debits:>12,.2f}')
        print(f'Actual Debits:     Rs.{total_debits:>12,.2f}')
        print(f'Difference:        Rs.{expected_debits - total_debits:>12,.2f}')
        print()
        print(f'Expected Balance:  Rs.{expected_balance:>12,.2f}')
        print(f'Actual Balance:    Rs.{total_credits - total_debits:>12,.2f}')
        print(f'Difference:        Rs.{expected_balance - (total_credits - total_debits):>12,.2f}')

if __name__ == "__main__":
    asyncio.run(analyze())

# Made with Bob
