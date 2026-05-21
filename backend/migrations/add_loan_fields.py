"""
Add loan-specific fields to financial_accounts table
Migration script to add loan tracking fields
"""
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.db.session import engine


async def upgrade():
    """Add loan-specific columns to financial_accounts table"""
    async with engine.begin() as conn:
        # Add loan-specific columns
        await conn.execute(text("""
            ALTER TABLE financial_accounts
            ADD COLUMN IF NOT EXISTS loan_principal NUMERIC(15, 2),
            ADD COLUMN IF NOT EXISTS loan_outstanding NUMERIC(15, 2),
            ADD COLUMN IF NOT EXISTS interest_rate NUMERIC(5, 2),
            ADD COLUMN IF NOT EXISTS emi_amount NUMERIC(15, 2),
            ADD COLUMN IF NOT EXISTS loan_tenure_months INTEGER,
            ADD COLUMN IF NOT EXISTS remaining_tenure_months INTEGER,
            ADD COLUMN IF NOT EXISTS loan_start_date TIMESTAMP WITH TIME ZONE,
            ADD COLUMN IF NOT EXISTS total_interest_paid NUMERIC(15, 2) DEFAULT 0.0,
            ADD COLUMN IF NOT EXISTS total_principal_paid NUMERIC(15, 2) DEFAULT 0.0;
        """))
        
        print("[SUCCESS] Added loan-specific fields to financial_accounts table")


async def downgrade():
    """Remove loan-specific columns from financial_accounts table"""
    async with engine.begin() as conn:
        await conn.execute(text("""
            ALTER TABLE financial_accounts
            DROP COLUMN IF EXISTS loan_principal,
            DROP COLUMN IF EXISTS loan_outstanding,
            DROP COLUMN IF EXISTS interest_rate,
            DROP COLUMN IF EXISTS emi_amount,
            DROP COLUMN IF EXISTS loan_tenure_months,
            DROP COLUMN IF EXISTS remaining_tenure_months,
            DROP COLUMN IF EXISTS loan_start_date,
            DROP COLUMN IF EXISTS total_interest_paid,
            DROP COLUMN IF EXISTS total_principal_paid;
        """))
        
        print("[SUCCESS] Removed loan-specific fields from financial_accounts table")


if __name__ == "__main__":
    import asyncio
    
    print("Running migration: Add loan fields to financial_accounts")
    asyncio.run(upgrade())
    print("Migration completed successfully!")

# Made with Bob
