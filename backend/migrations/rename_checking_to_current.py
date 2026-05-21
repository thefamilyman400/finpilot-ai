"""
Migration: Rename CHECKING account type to CURRENT
Updates all existing checking accounts to current accounts
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import AsyncSessionLocal
from sqlalchemy import text

async def migrate():
    async with AsyncSessionLocal() as db:
        print("Starting migration: Rename CHECKING to CURRENT...")
        
        # Update account_type from 'checking' to 'current'
        result = await db.execute(
            text("UPDATE financial_accounts SET account_type = 'current' WHERE account_type = 'checking'")
        )
        
        rows_updated = result.rowcount
        await db.commit()
        
        print(f"[SUCCESS] Migration complete: Updated {rows_updated} accounts from 'checking' to 'current'")

if __name__ == "__main__":
    asyncio.run(migrate())

# Made with Bob
