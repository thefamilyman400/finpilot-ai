"""
Script to delete ALL accounts and transactions to start fresh
This will allow you to test the 6-month expense calculation from scratch
"""
import asyncio
from sqlalchemy import delete
from app.db.session import AsyncSessionLocal
from app.models.transaction import Transaction
from app.models.account import FinancialAccount


async def reset_all_data():
    """Delete all accounts and transactions"""
    async with AsyncSessionLocal() as db:
        try:
            print("\n🔍 Checking database...")
            
            # Delete all transactions first (foreign key constraint)
            result = await db.execute(delete(Transaction))
            trans_count = result.rowcount
            print(f"✅ Deleted {trans_count} transaction(s)")
            
            # Delete all accounts
            result = await db.execute(delete(FinancialAccount))
            acc_count = result.rowcount
            print(f"✅ Deleted {acc_count} account(s)")
            
            await db.commit()
            
            print(f"\n✨ Database reset complete!")
            print(f"   - {acc_count} accounts removed")
            print(f"   - {trans_count} transactions removed")
            print(f"\n📝 You can now:")
            print(f"   1. Import bank statements for the last 6 months")
            print(f"   2. Test the monthly expense calculation")
            print(f"   3. The system will average all debit transactions over 6 months (180 days)")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            await db.rollback()


if __name__ == "__main__":
    print("\n⚠️  WARNING: This will delete ALL accounts and transactions!")
    confirm = input("Type 'DELETE ALL' to confirm: ")
    
    if confirm == 'DELETE ALL':
        asyncio.run(reset_all_data())
    else:
        print("❌ Operation cancelled. Database unchanged.")

# Made with Bob
