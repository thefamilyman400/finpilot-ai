"""
Delete all financial accounts and transactions
"""
import asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import select, delete
from app.models.account import FinancialAccount
from app.models.transaction import Transaction

async def delete_all():
    async with AsyncSessionLocal() as db:
        print("\n=== Deleting All Accounts and Transactions ===\n")
        
        # Delete all transactions first (foreign key constraint)
        result = await db.execute(delete(Transaction))
        tx_count = result.rowcount
        print(f"Deleted {tx_count} transactions")
        
        # Delete all accounts
        result = await db.execute(delete(FinancialAccount))
        acc_count = result.rowcount
        print(f"Deleted {acc_count} accounts")
        
        await db.commit()
        
        print(f"\n[SUCCESS] All accounts and transactions deleted!")
        print(f"Total deleted: {acc_count} accounts, {tx_count} transactions")

if __name__ == "__main__":
    asyncio.run(delete_all())

# Made with Bob
