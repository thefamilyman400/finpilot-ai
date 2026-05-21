import asyncio
from app.db.session import AsyncSessionLocal
from app.models.account import FinancialAccount
from app.models.transaction import Transaction
from sqlalchemy import select, delete

async def delete_hdfc_data():
    async with AsyncSessionLocal() as db:
        # Find the HDFC account
        result = await db.execute(
            select(FinancialAccount).where(
                FinancialAccount.institution_name == "HDFC"
            )
        )
        hdfc_account = result.scalar_one_or_none()
        
        if not hdfc_account:
            print("No HDFC account found!")
            return
        
        account_id = hdfc_account.id
        print(f"\nFound HDFC Account:")
        print(f"Account Name: {hdfc_account.account_name}")
        print(f"Account Number: ****{hdfc_account.account_number_last4}")
        print(f"Balance: Rs.{hdfc_account.balance:,.2f}")
        print(f"Account ID: {account_id}")
        
        # Count transactions
        trans_result = await db.execute(
            select(Transaction).where(Transaction.account_id == account_id)
        )
        transactions = trans_result.scalars().all()
        trans_count = len(transactions)
        
        print(f"\nTransactions to delete: {trans_count}")
        print("\nDeleting...")
        
        # Delete all transactions for this account
        await db.execute(
            delete(Transaction).where(Transaction.account_id == account_id)
        )
        
        # Delete the account
        await db.delete(hdfc_account)
        
        await db.commit()
        
        print(f"\nSUCCESS!")
        print(f"- Deleted {trans_count} transactions")
        print(f"- Deleted HDFC account")
        print(f"\nYou can now upload the bank statement again for a fresh start.")

if __name__ == "__main__":
    asyncio.run(delete_hdfc_data())

# Made with Bob
