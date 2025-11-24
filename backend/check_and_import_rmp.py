"""Check if database has RMP data and import if missing."""
import asyncio
from pathlib import Path
from billiken_blueprint import services
from billiken_blueprint.repositories.instructor_repository import InstructorRepository


async def check_and_import_if_needed():
    """Check if RMP data exists, and import if not."""
    from pathlib import Path
    from sqlalchemy.exc import OperationalError
    
    db_path = Path("data/data.db")
    
    # If database doesn't exist, skip check (migrations will create it)
    if not db_path.exists():
        print("⚠ Database not found. Run migrations first.")
        return
    
    instructor_repo = InstructorRepository(services.async_sessionmaker)
    
    # Check if we have any instructors with RMP ratings
    try:
        all_instructors = await instructor_repo.get_all()
        has_rmp_data = any(instructor.rmp_rating is not None for instructor in all_instructors)
    except OperationalError as e:
        # Database exists but tables might not be created yet
        if "no such table" in str(e).lower():
            print("⚠ Database tables not found. Run migrations first.")
            return
        raise
    
    if has_rmp_data:
        print("✓ RMP data already exists in database")
        return
    
    print("⚠ No RMP data found in database. Checking for import files...")
    
    # Check if JSON files exist
    script_dir = Path(__file__).parent
    json_files = [
        script_dir / "cs_professors_with_reviews.json",
        script_dir / "math_professors_with_reviews.json",
        Path("/app/cs_professors_with_reviews.json"),
        Path("/app/math_professors_with_reviews.json"),
    ]
    
    json_file_exists = any(f.exists() for f in json_files)
    
    if not json_file_exists:
        print("⚠ RMP JSON files not found. Skipping import.")
        print("  To import RMP data, ensure JSON files are available and run:")
        print("  uv run python import_rmp_ratings.py")
        return
    
    print("📥 Importing RMP data...")
    try:
        from import_rmp_ratings import import_rmp_ratings
        await import_rmp_ratings()
        print("✓ RMP data import completed")
    except Exception as e:
        print(f"⚠ Error importing RMP data: {e}")
        print("  You can manually run: uv run python import_rmp_ratings.py")


if __name__ == "__main__":
    asyncio.run(check_and_import_if_needed())

