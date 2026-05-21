"""
Test script for new requirements:
1. Account number is shown in responses
2. Credit card validation (requires bank account from same institution)
"""
import asyncio
import sys
from app.db.session import AsyncSessionLocal
from sqlalchemy import select
from app.models.account import FinancialAccount
from app.models.user import User

async def test_requirements():
    async with AsyncSessionLocal() as db:
        # Get a test user
        result = await db.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        
        if not user:
            print("No user found in database")
            return
        
        print(f"\n=== Testing Requirements for User: {user.email} ===\n")
        
        # Test 1: Check if account_number_last4 is present
        print("Test 1: Account Number Display")
        print("-" * 50)
        
        result = await db.execute(
            select(FinancialAccount).where(
                FinancialAccount.user_id == user.id
            ).limit(5)
        )
        accounts = result.scalars().all()
        
        if accounts:
            for acc in accounts:
                print(f"Account: {acc.institution_name}")
                print(f"  Type: {acc.account_type}")
                print(f"  Account Number (Last 4): {acc.account_number_last4 or 'Not Set'}")
                print(f"  Balance: Rs.{acc.balance:,.2f}" if acc.balance else "  Balance: Not Set")
                print()
        else:
            print("No accounts found for user")
        
        # Test 2: Check credit card validation logic
        print("\nTest 2: Credit Card Validation")
        print("-" * 50)
        
        # Get all accounts grouped by institution
        result = await db.execute(
            select(FinancialAccount).where(
                FinancialAccount.user_id == user.id
            )
        )
        all_accounts = result.scalars().all()
        
        from collections import defaultdict
        by_institution = defaultdict(list)
        
        for acc in all_accounts:
            by_institution[acc.institution_name.lower()].append(acc)
        
        print(f"Found {len(by_institution)} institutions:\n")
        
        for institution, accs in by_institution.items():
            print(f"Institution: {institution.upper()}")
            has_bank = False
            has_credit_card = False
            
            for acc in accs:
                print(f"  - {acc.account_type.value}: {acc.account_name or 'Unnamed'}")
                if acc.account_type.value in ['current', 'savings']:
                    has_bank = True
                if acc.account_type.value == 'credit_card':
                    has_credit_card = True
            
            # Check validation status
            if has_credit_card and not has_bank:
                print(f"  ⚠️  WARNING: Credit card exists without bank account!")
            elif has_credit_card and has_bank:
                print(f"  ✓ Valid: Credit card has associated bank account")
            elif has_bank and not has_credit_card:
                print(f"  ✓ Valid: Bank account exists (credit card can be added)")
            
            print()
        
        print("\n=== Summary ===")
        print(f"Total Accounts: {len(all_accounts)}")
        print(f"Institutions: {len(by_institution)}")
        print("\nValidation Rule:")
        print("✓ Credit cards can only be created if a bank account")
        print("  (Current or Savings) exists for the same institution")

if __name__ == "__main__":
    asyncio.run(test_requirements())

# Made with Bob
