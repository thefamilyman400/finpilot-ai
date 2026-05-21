"""
Check loan account details in detail
"""
import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.account import FinancialAccount, AccountType
from app.models.user import User


async def check_loans():
    """Check loan details"""
    async with AsyncSessionLocal() as db:
        # Get the specific user
        result = await db.execute(
            select(User).where(User.email == "you@example.com")
        )
        user = result.scalars().first()
        
        if not user:
            print("[ERROR] User not found")
            return
        
        print(f"[USER] {user.email}\n")
        
        # Get loan accounts
        result = await db.execute(
            select(FinancialAccount).where(
                FinancialAccount.user_id == user.id,
                FinancialAccount.account_type == AccountType.LOAN
            )
        )
        loans = result.scalars().all()
        
        print(f"Total Loan Accounts: {len(loans)}\n")
        
        for loan in loans:
            print(f"Loan: {loan.institution_name}")
            print(f"  ID: {loan.id}")
            print(f"  Active: {loan.is_active}")
            print(f"  Principal: {loan.loan_principal}")
            print(f"  Outstanding: {loan.loan_outstanding}")
            print(f"  Interest Rate: {loan.interest_rate}")
            print(f"  EMI Amount: {loan.emi_amount}")
            print(f"  Tenure: {loan.loan_tenure_months}")
            print(f"  Remaining: {loan.remaining_tenure_months}")
            print(f"  Start Date: {loan.loan_start_date}")
            print()


if __name__ == "__main__":
    asyncio.run(check_loans())

# Made with Bob
