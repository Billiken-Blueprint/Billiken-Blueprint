"""Check if database has courses and seed if missing."""
import asyncio
from pathlib import Path
from billiken_blueprint import services
from billiken_blueprint.repositories.course_repository import CourseRepository
from sqlalchemy.exc import OperationalError


async def check_and_seed_courses_if_needed():
    """Check if courses exist, and seed if not."""
    from pathlib import Path
    
    db_path = Path("data/data.db")
    
    # If database doesn't exist, skip check (migrations will create it)
    if not db_path.exists():
        print("⚠ Database not found. Run migrations first.")
        return
    
    course_repo = CourseRepository(services.async_sessionmaker)
    
    # Check if we have any courses
    try:
        courses = await course_repo.get_all()
        if len(courses) > 0:
            print(f"✓ Courses already exist in database ({len(courses)} courses)")
            return
    except OperationalError as e:
        # Database exists but tables might not be created yet
        if "no such table" in str(e).lower():
            print("⚠ Database tables not found. Run migrations first.")
            return
        raise
    
    print("⚠ No courses found in database. Attempting to seed courses...")
    
    # Try to seed courses
    try:
        from get_courses import main as seed_courses
        await seed_courses()
        # Check again
        courses = await course_repo.get_all()
        if len(courses) > 0:
            print(f"✓ Courses seeded successfully ({len(courses)} courses)")
        else:
            print("⚠ Course seeding completed but no courses found. This may be normal if course API is unavailable.")
    except Exception as e:
        print(f"⚠ Error seeding courses: {e}")
        print("  Courses will need to be seeded manually or via course API")


if __name__ == "__main__":
    asyncio.run(check_and_seed_courses_if_needed())

