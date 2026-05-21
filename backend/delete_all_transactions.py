"""
Script to delete all transactions from the database
"""
import asyncio
from sqlalchemy import select, delete
from app.db.session import AsyncSessionLocal
from app.models.transaction import Transaction


async def delete_all_transactions():
    """Delete all transactions from the database"""
    async with AsyncSessionLocal() as db:
        try:
            # Get count before deletion
            result = await db.execute(select(Transaction))
            transactions = result.scalars().all()
            count = len(transactions)
            
            if count == 0:
                print("No transactions found in the database.")
                return
            
            print(f"Found {count} transactions in the database.")
            confirm = input(f"Are you sure you want to delete all {count} transactions? (yes/no): ")
            
            if confirm.lower() != 'yes':
                print("Deletion cancelled.")
                return
            
            # Delete all transactions
            await db.execute(delete(Transaction))
            await db.commit()
            
            print(f"✅ Successfully deleted all {count} transactions!")
            
        except Exception as e:
            print(f"❌ Error deleting transactions: {str(e)}")
            await db.rollback()


if __name__ == "__main__":
    asyncio.run(delete_all_transactions())

# Made with Bob
