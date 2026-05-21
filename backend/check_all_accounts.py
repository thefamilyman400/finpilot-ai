"""
Check ALL accounts in database for ALL users
"""
import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.account import FinancialAccount
from app.models.user import User


async def check_all():
    """Check all accounts for all users"""
    async with AsyncSessionLocal() as db:
        # Get ALL users
        result = await db.execute(select(User))
        users = result.scalars().all()
        
        print(f"Total Users: {len(users)}\n")
        
        for user in users:
            print(f"[USER] {user.email} (ID: {user.id})")
            
            # Get ALL accounts for this user
            result = await db.execute(
                select(FinancialAccount).where(
                    FinancialAccount.user_id == user.id
                )
            )
            accounts = result.scalars().all()
            
            print(f"  Total Accounts: {len(accounts)}\n")
            
            if len(accounts) == 0:
                print("  [NO ACCOUNTS]\n")
                continue
            
            for acc in accounts:
                print(f"  Account: {acc.account_name or acc.institution_name}")
                print(f"    Type: {acc.account_type}")
                print(f"    Active: {acc.is_active}")
                print(f"    Balance: Rs.{float(acc.balance) if acc.balance else 0:,.2f}")
                
                if acc.account_type.value == 'LOAN':
                    print(f"    --- LOAN DETAILS ---")
                    print(f"    Principal: Rs.{float(acc.loan_principal) if acc.loan_principal else 0:,.2f}")
                    print(f"    Outstanding: Rs.{float(acc.loan_outstanding) if acc.loan_outstanding else 0:,.2f}")
                    print(f"    Interest Rate: {float(acc.interest_rate) if acc.interest_rate else 0}%")
                    print(f"    EMI Amount: Rs.{float(acc.emi_amount) if acc.emi_amount else 0:,.2f}")
                    print(f"    Tenure: {acc.loan_tenure_months} months")
                    print(f"    Remaining: {acc.remaining_tenure_months} months")
                
                print()


if __name__ == "__main__":
    asyncio.run(check_all())

# Made with Bob
