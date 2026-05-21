"""
Script to delete all savings accounts and their transactions from the database
"""
import asyncio
from sqlalchemy import select, delete
from app.db.session import AsyncSessionLocal
from app.models.transaction import Transaction
from app.models.account import FinancialAccount, AccountType


async def delete_savings_and_transactions():
    """Delete all savings accounts and their transactions from the database"""
    async with AsyncSessionLocal() as db:
        try:
            # Get all savings accounts
            result = await db.execute(
                select(FinancialAccount).where(
                    FinancialAccount.account_type == AccountType.SAVINGS
                )
            )
            savings_accounts = result.scalars().all()
            
            if not savings_accounts:
                print("No savings accounts found in the database.")
                return
            
            account_ids = [acc.id for acc in savings_accounts]
            print(f"\nFound {len(savings_accounts)} savings account(s):")
            for acc in savings_accounts:
                print(f"  - {acc.account_name or acc.institution_name} (Balance: ₹{acc.balance})")
            
            # Get transactions for these accounts
            trans_result = await db.execute(
                select(Transaction).where(
                    Transaction.account_id.in_(account_ids)
                )
            )
            transactions = trans_result.scalars().all()
            trans_count = len(transactions)
            
            print(f"\nFound {trans_count} transaction(s) associated with these accounts.")
            
            confirm = input(f"\nAre you sure you want to delete {len(savings_accounts)} savings account(s) and {trans_count} transaction(s)? (yes/no): ")
            
            if confirm.lower() != 'yes':
                print("Deletion cancelled.")
                return
            
            # Delete transactions first (foreign key constraint)
            if trans_count > 0:
                await db.execute(
                    delete(Transaction).where(
                        Transaction.account_id.in_(account_ids)
                    )
                )
                print(f"✅ Deleted {trans_count} transaction(s)")
            
            # Delete savings accounts
            await db.execute(
                delete(FinancialAccount).where(
                    FinancialAccount.account_type == AccountType.SAVINGS
                )
            )
            
            await db.commit()
            
            print(f"✅ Successfully deleted {len(savings_accounts)} savings account(s)!")
            print("\n✨ All savings accounts and their transactions have been removed.")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            await db.rollback()


if __name__ == "__main__":
    asyncio.run(delete_savings_and_transactions())

# Made with Bob
