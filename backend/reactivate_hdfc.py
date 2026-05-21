import asyncio
from app.db.session import AsyncSessionLocal
from app.models.account import FinancialAccount
from sqlalchemy import select, update

async def reactivate_hdfc():
    async with AsyncSessionLocal() as db:
        # Find the HDFC account
        result = await db.execute(
            select(FinancialAccount).where(
                FinancialAccount.institution_name == "HDFC"
            )
        )
        hdfc_account = result.scalar_one_or_none()
        
        if not hdfc_account:
            print("❌ HDFC account not found!")
            return
        
        print(f"\n{'='*80}")
        print(f"Found HDFC Account:")
        print(f"{'='*80}")
        print(f"Account Name: {hdfc_account.account_name}")
        print(f"Account Number: ****{hdfc_account.account_number_last4}")
        print(f"Balance: Rs.{hdfc_account.balance:,.2f}")
        print(f"Currently Active: {hdfc_account.is_active}")
        print(f"{'='*80}\n")
        
        if hdfc_account.is_active:
            print("✅ Account is already active!")
        else:
            # Reactivate the account
            hdfc_account.is_active = True
            await db.commit()
            print("✅ HDFC account has been reactivated!")
            print(f"The account will now appear in the UI.")

if __name__ == "__main__":
    asyncio.run(reactivate_hdfc())

# Made with Bob
