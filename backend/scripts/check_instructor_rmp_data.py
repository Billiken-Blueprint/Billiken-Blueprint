"""Debug script to check if instructors have RMP data populated."""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path so we can import billiken_blueprint
sys.path.insert(0, str(Path(__file__).parent.parent))

from billiken_blueprint import services


async def check_instructor_rmp_data():
    """Check which instructors have RMP data and which don't."""
    print("Checking instructor RMP data...")
    print("=" * 60)
    
    try:
        all_instructors = await services.instructor_repository.get_all()
    except Exception as e:
        if "no such table" in str(e).lower():
            print("❌ ERROR: Database tables don't exist!")
            print("   You need to run migrations first:")
            print("   uv run alembic upgrade head")
            return
        else:
            raise
    print(f"Total instructors in database: {len(all_instructors)}")
    print()
    
    instructors_with_rmp = []
    instructors_without_rmp = []
    
    for instructor in all_instructors:
        if instructor.rmp_rating is not None:
            instructors_with_rmp.append(instructor)
        else:
            instructors_without_rmp.append(instructor)
    
    print(f"Instructors WITH RMP rating: {len(instructors_with_rmp)}")
    if instructors_with_rmp:
        print("  Examples:")
        for inst in instructors_with_rmp[:5]:
            print(f"    - {inst.name}: rating={inst.rmp_rating}, num_ratings={inst.rmp_num_ratings}, dept={inst.department}")
    print()
    
    print(f"Instructors WITHOUT RMP rating: {len(instructors_without_rmp)}")
    if instructors_without_rmp:
        print("  Examples:")
        for inst in instructors_without_rmp[:10]:
            print(f"    - {inst.name}: dept={inst.department}")
    print()
    
    print("=" * 60)
    if len(instructors_with_rmp) == 0:
        print("⚠️  WARNING: No instructors have RMP rating data!")
        print("   This means ratings will not show up.")
        print("   Run: uv run scripts/update_instructor_rmp_data.py")
    else:
        print(f"✓ {len(instructors_with_rmp)} instructors have RMP data - ratings should show")


if __name__ == "__main__":
    asyncio.run(check_instructor_rmp_data())

