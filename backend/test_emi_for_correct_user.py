"""
Test EMI fetch for you@example.com user
"""
import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.services.simulation_service import SimulationService
from app.models.user import User


async def test():
    """Test EMI data fetch for correct user"""
    async with AsyncSessionLocal() as db:
        # Get the correct user
        result = await db.execute(
            select(User).where(User.email == "you@example.com")
        )
        user = result.scalars().first()
        
        if not user:
            print("[ERROR] User not found")
            return
        
        print(f"[OK] Testing for user: {user.email}")
        print(f"     User ID: {user.id}\n")
        
        # Fetch spending data
        service = SimulationService()
        spending_data = await service.get_user_spending_data(db, user.id)
        
        print("Spending Data Results:")
        print(f"  Has Data: {spending_data.get('has_data')}")
        print(f"  Monthly Income: Rs.{spending_data.get('monthly_income', 0):,.2f}")
        print(f"  Monthly Expenses: Rs.{spending_data.get('monthly_expenses', 0):,.2f}")
        print(f"  Total Monthly EMI: Rs.{spending_data.get('total_monthly_emi', 0):,.2f}")
        print(f"  Loan Count: {spending_data.get('loan_count', 0)}")
        print(f"  Available for Investment: Rs.{spending_data.get('available_for_investment', 0):,.2f}")
        
        if spending_data.get('loan_count', 0) > 0:
            print(f"\nLoan Details:")
            for loan in spending_data.get('loan_accounts', []):
                print(f"  - {loan.get('account_name')}")
                print(f"    EMI: Rs.{loan.get('emi_amount', 0):,.2f}")
                print(f"    Outstanding: Rs.{loan.get('outstanding', 0):,.2f}")
        else:
            print(f"\n[WARNING] No active loans found!")


if __name__ == "__main__":
    asyncio.run(test())

# Made with Bob
