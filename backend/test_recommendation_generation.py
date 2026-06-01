import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.services.recommendation_service import recommendation_service
from app.services.ai_service import ai_service
from config import settings

async def test_recommendation_generation():
    # Create database session
    engine = create_async_engine(settings.database_url_async, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        try:
            # Get a user ID (you'll need to replace this with an actual user ID)
            print("Testing recommendation generation...")
            print(f"Using model: {recommendation_service.model}")
            print(f"API key present: {bool(recommendation_service.api_key)}")
            
            # Build financial context first
            print("\nBuilding financial context...")
            context = await ai_service.build_financial_context(db, "YOUR_USER_ID_HERE")
            print(f"Context: {context}")
            
            if not context or not context.get('account_count'):
                print("\nERROR: No financial data found. Need accounts and transactions.")
                return
            
            # Try to generate recommendations
            print("\nGenerating recommendations...")
            recommendations = await recommendation_service.generate_recommendations(
                db=db,
                user_id="YOUR_USER_ID_HERE",
                focus_areas=None,
                max_recommendations=3
            )
            
            print(f"\nSuccess! Generated {len(recommendations)} recommendations:")
            for rec in recommendations:
                print(f"  - {rec.title}")
                
        except Exception as e:
            print(f"\nERROR: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_recommendation_generation.py <user_id>")
        print("Example: python test_recommendation_generation.py 123e4567-e89b-12d3-a456-426614174000")
        sys.exit(1)
    
    user_id = sys.argv[1]
    
    # Replace placeholder with actual user ID
    import re
    script_content = open(__file__).read()
    script_content = script_content.replace("YOUR_USER_ID_HERE", user_id)
    exec(script_content.split('if __name__')[0] + f'\nasyncio.run(test_recommendation_generation())')

# Made with Bob
