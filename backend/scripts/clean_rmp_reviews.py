"""Remove RMP reviews from the database to reduce size.

RMP reviews are now loaded from JSON files automatically, so they don't need to be in the database.
This script removes them to reduce database size.
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path so we can import billiken_blueprint
sys.path.insert(0, str(Path(__file__).parent.parent))

from billiken_blueprint import services
from sqlalchemy import delete
from billiken_blueprint.repositories.rmp_review_repository import DBRmpReview


async def clean_rmp_reviews():
    """Remove all RMP reviews from the database."""
    print("Cleaning RMP reviews from database...")
    
    from sqlalchemy.ext.asyncio import AsyncSession
    async with services.async_sessionmaker() as session:
        # Count existing reviews
        from sqlalchemy import select, func
        count_stmt = select(func.count(DBRmpReview.id))
        result = await session.execute(count_stmt)
        count = result.scalar() or 0
        
        if count == 0:
            print("  No RMP reviews found in database.")
            return
        
        print(f"  Found {count} RMP reviews to remove...")
        
        # Delete all RMP reviews
        delete_stmt = delete(DBRmpReview)
        await session.execute(delete_stmt)
        await session.commit()
        
        print(f"  ✓ Removed {count} RMP reviews from database")
        print("  Note: RMP reviews will now be loaded from JSON files automatically")


if __name__ == "__main__":
    asyncio.run(clean_rmp_reviews())

