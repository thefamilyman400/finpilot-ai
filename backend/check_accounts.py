import asyncio
from app.db.session import AsyncSessionLocal
from app.models.account import FinancialAccount
from sqlalchemy import select

async def check_accounts():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(FinancialAccount))
        accounts = result.scalars().all()
        
        print(f"\n{'='*80}")
        print(f"Total accounts in database: {len(accounts)}")
        print(f"{'='*80}\n")
        
        for acc in accounts:
            print(f"Institution: {acc.institution_name}")
            print(f"Account Name: {acc.account_name}")
            print(f"Account Number: ****{acc.account_number_last4}")
            print(f"Account ID: {acc.id}")
            print(f"Active: {acc.is_active}")
            print(f"Balance: Rs.{acc.balance:,.2f}")
            print(f"Created: {acc.created_at}")
            print(f"Updated: {acc.updated_at}")
            print("-" * 80)

if __name__ == "__main__":
    asyncio.run(check_accounts())

# Made with Bob
