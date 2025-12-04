"""Build a seed database with essential data (courses, instructors) but no RMP reviews.

This creates a clean, small database that can be used for fresh setups.
RMP reviews are loaded from JSON files automatically, so they don't need to be in the database.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import billiken_blueprint
sys.path.insert(0, str(Path(__file__).parent.parent))

from dump_data import base_path
import json


async def build_seed_database():
    """Build a clean seed database with essential data."""
    print("Building seed database...")
    
    # Ensure data directory exists
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Remove existing database if it exists
    db_path = data_dir / "data.db"
    if db_path.exists():
        print(f"Removing existing database at {db_path}")
        db_path.unlink()
    
    # Create new database with migrations
    print("Running database migrations...")
    from alembic.config import Config
    from alembic import command
    
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    
    # Now import services after database is created
    # We need to reimport to get fresh connections
    import importlib
    import billiken_blueprint.services
    importlib.reload(billiken_blueprint.services)
    from billiken_blueprint import services
    from billiken_blueprint.domain.courses.course import Course
    from billiken_blueprint.domain.degrees.degree import Degree
    from billiken_blueprint.domain.section import Section
    from billiken_blueprint.domain.instructor import Professor
    from billiken_blueprint.domain.courses.course_attribute import CourseAttribute
    
    print("Importing courses...")
    # Import courses
    with open(os.path.join(base_path, "courses.json"), "r") as f:
        courses_data = json.load(f)
    for course_dict in courses_data:
        await services.course_repository.save(Course.from_dict(course_dict))
    print(f"  Imported {len(courses_data)} courses")
    
    print("Importing instructors...")
    # Import instructors
    with open(os.path.join(base_path, "instructors.json"), "r") as f:
        instructors_data = json.load(f)
    for instructor_dict in instructors_data:
        await services.instructor_repository.save(Professor.from_dict(instructor_dict))
    print(f"  Imported {len(instructors_data)} instructors")
    
    print("Importing sections...")
    # Import sections
    with open(os.path.join(base_path, "sections.json"), "r") as f:
        sections_data = json.load(f)
    for section_dict in sections_data:
        await services.section_repository.save(Section.from_dict(section_dict))
    print(f"  Imported {len(sections_data)} sections")
    
    print("Importing degrees...")
    # Import degrees
    with open(os.path.join(base_path, "degrees.json"), "r") as f:
        degrees_data = json.load(f)
    for degree_dict in degrees_data:
        await services.degree_repository.save(Degree.from_dict(degree_dict))
    print(f"  Imported {len(degrees_data)} degrees")
    
    print("Importing course attributes...")
    # Import course attributes
    with open(os.path.join(base_path, "attributes.json"), "r") as f:
        attributes_data = json.load(f)
    for attribute_dict in attributes_data:
        await services.course_attribute_repository.save(
            CourseAttribute.from_dict(attribute_dict)
        )
    print(f"  Imported {len(attributes_data)} course attributes")
    
    print("\nUpdating instructor RMP data...")
    # Update instructor RMP rating fields (needed for ratings to show)
    from scripts.update_instructor_rmp_data import update_instructor_rmp_data
    await update_instructor_rmp_data()
    
    # Note: Individual RMP reviews are NOT imported - they're loaded from JSON files automatically
    
    # Get final database size
    if db_path.exists():
        size_kb = db_path.stat().st_size / 1024
        print(f"\n✓ Seed database created successfully!")
        print(f"  Location: {db_path.absolute()}")
        print(f"  Size: {size_kb:.1f} KB")
        print(f"\nNote: RMP reviews are loaded from JSON files automatically, so they're not in the database.")


if __name__ == "__main__":
    asyncio.run(build_seed_database())

