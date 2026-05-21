"""
Initialize FinPilot AI Database
Creates all tables for the complete application
Run this once to set up the database schema
"""
import asyncio
from sqlalchemy import text
from app.db.session import engine
from app.db.base import Base

# Import all models to ensure they're registered with Base
from app.models.user import User
from app.models.account import FinancialAccount
from app.models.transaction import Transaction
from app.models.conversation import Conversation, Message
from app.models.recommendation import Recommendation
from app.models.document import Document
from app.models.simulation import FinancialSimulation
from app.models.workflow import AutonomousWorkflow, WorkflowExecution


async def create_tables():
    """Create all database tables"""
    print("=" * 60)
    print("FinPilot AI - Database Initialization")
    print("=" * 60)
    print("\n[INFO] Creating all database tables...")
    
    async with engine.begin() as conn:
        # Create all tables defined in models
        await conn.run_sync(Base.metadata.create_all)
    
    print("\n[SUCCESS] All tables created successfully!")
    print("\nTables created:")
    print("  ✓ users")
    print("  ✓ financial_accounts")
    print("  ✓ transactions")
    print("  ✓ conversations")
    print("  ✓ messages")
    print("  ✓ recommendations")
    print("  ✓ documents")
    print("  ✓ financial_simulations")
    print("  ✓ autonomous_workflows")
    print("  ✓ workflow_executions")


async def verify_tables():
    """Verify that all tables were created"""
    print("\n[INFO] Verifying tables...")
    
    expected_tables = [
        'users',
        'financial_accounts',
        'transactions',
        'conversations',
        'messages',
        'recommendations',
        'documents',
        'financial_simulations',
        'autonomous_workflows',
        'workflow_executions'
    ]
    
    async with engine.begin() as conn:
        # Check if tables exist
        result = await conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = ANY(:table_names)
            ORDER BY table_name
        """), {"table_names": expected_tables})
        
        tables = [row[0] for row in result]
        
        if len(tables) == len(expected_tables):
            print(f"\n[SUCCESS] All {len(tables)} tables verified:")
            for table in tables:
                print(f"  ✓ {table}")
        else:
            missing = set(expected_tables) - set(tables)
            print(f"\n[WARNING] Expected {len(expected_tables)} tables, found {len(tables)}")
            print(f"  Found: {', '.join(tables)}")
            if missing:
                print(f"  Missing: {', '.join(missing)}")


async def get_table_info():
    """Display table information"""
    print("\n[INFO] Database schema information:")
    
    async with engine.begin() as conn:
        result = await conn.execute(text("""
            SELECT 
                table_name,
                (SELECT COUNT(*) 
                 FROM information_schema.columns 
                 WHERE table_schema = 'public' 
                 AND table_name = t.table_name) as column_count
            FROM information_schema.tables t
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        
        print("\n  Table Name                    | Columns")
        print("  " + "-" * 50)
        for table_name, column_count in result:
            print(f"  {table_name:<30} | {column_count}")


async def main():
    """Main function"""
    try:
        await create_tables()
        await verify_tables()
        await get_table_info()
        
        print("\n" + "=" * 60)
        print("[SUCCESS] Database initialization complete!")
        print("=" * 60)
        print("\nYou can now start the application:")
        print("  python main.py")
        print("\nOr run with uvicorn:")
        print("  uvicorn main:app --reload")
        print("\n" + "=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"[ERROR] Database initialization failed: {e}")
        print("=" * 60)
        print("\nPlease check:")
        print("  1. PostgreSQL is running")
        print("  2. Database credentials in .env are correct")
        print("  3. Database exists (create it if needed)")
        print("=" * 60)
        raise


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob