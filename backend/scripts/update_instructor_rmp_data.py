"""Update instructor records with RMP rating data from JSON files.

This updates the instructor table with aggregated RMP data (rating, num_ratings, url)
but does NOT import individual reviews (those load from files automatically).
"""

import asyncio
import json
import re
from pathlib import Path
import sys

# Add the parent directory to the path so we can import billiken_blueprint
sys.path.insert(0, str(Path(__file__).parent.parent))

from billiken_blueprint import services
from billiken_blueprint.domain.instructor import Professor


async def update_instructor_rmp_data():
    """Update instructor records with RMP aggregated data from JSON files."""
    print("Updating instructor RMP data from JSON files...")

    # Define possible paths for RMP data
    cs_possible_paths = [
        Path("data_dumps/cs_professors_with_reviews.json"),
        Path("data_dumps/cs_professors.json"),
    ]

    math_possible_paths = [
        Path("data_dumps/math_professors_with_reviews.json"),
        Path("data_dumps/math_professors.json"),
    ]

    # Load CS professors
    cs_file = None
    for path in cs_possible_paths:
        if path.exists():
            cs_file = path
            break

    # Load Math professors
    math_file = None
    for path in math_possible_paths:
        if path.exists():
            math_file = path
            break

    # Load RMP data
    rmp_data = []

    if cs_file and cs_file.exists():
        print(f"Loading CS RMP data from: {cs_file}")
        with open(cs_file, "r") as f:
            cs_data = json.load(f)
            for prof in cs_data:
                prof["_department"] = "CSCI"
            rmp_data.extend(cs_data)
            print(f"Loaded {len(cs_data)} CS professor records")

    if math_file and math_file.exists():
        print(f"Loading Math RMP data from: {math_file}")
        with open(math_file, "r") as f:
            math_data = json.load(f)
            for prof in math_data:
                prof["_department"] = "MATH"
            rmp_data.extend(math_data)
            print(f"Loaded {len(math_data)} Math professor records")

    if not rmp_data:
        print("No RMP data found. Make sure data_dumps/*.json files exist.")
        return

    print(f"Total RMP professor records: {len(rmp_data)}")

    # Get all existing instructors
    existing_instructors = await services.instructor_repository.get_all()
    instructor_by_name = {
        instructor.name.lower(): instructor for instructor in existing_instructors
    }

    matched = 0
    not_matched = []

    for rmp_prof in rmp_data:
        name = rmp_prof.get("name", "").strip()
        if not name:
            continue

        dept_from_prof = rmp_prof.get("_department")

        # Try exact match first
        instructor = instructor_by_name.get(name.lower())

        # If no exact match, try partial matches
        if not instructor:
            rmp_name_parts = name.lower().split()
            for existing_name, existing_instructor in instructor_by_name.items():
                existing_parts = existing_name.split()
                # Match if last names match
                if (
                    rmp_name_parts
                    and existing_parts
                    and rmp_name_parts[-1] == existing_parts[-1]
                ):
                    rmp_first = rmp_name_parts[0] if rmp_name_parts else ""
                    existing_first = existing_parts[0] if existing_parts else ""
                    if (
                        rmp_first == existing_first
                        or rmp_first.startswith(existing_first)
                        or existing_first.startswith(rmp_first)
                        or (
                            rmp_first in ["greg", "jim", "jimmy"]
                            and existing_first in ["gregory", "james"]
                        )
                        or (
                            existing_first in ["greg", "jim", "jimmy"]
                            and rmp_first in ["gregory", "james"]
                        )
                    ):
                        instructor = existing_instructor
                        break
                # Also try substring matching
                if name.lower() in existing_name or existing_name in name.lower():
                    instructor = existing_instructor
                    break

        if instructor:
            # Update instructor with RMP aggregated data only
            department = dept_from_prof or instructor.department

            # Normalize name for Ted Ahn
            instructor_name = instructor.name
            if "ahn" in name.lower() and (
                "ted" in name.lower() or "tae" in name.lower()
            ):
                instructor_name = "Ted Ahn"
            elif "ahn" in instructor.name.lower() and (
                "tae" in instructor.name.lower() and "ted" not in instructor.name.lower()
            ):
                instructor_name = "Ted Ahn"

            updated_instructor = Professor(
                id=instructor.id,
                name=instructor_name,
                rmp_rating=rmp_prof.get("overall_rating"),
                rmp_num_ratings=rmp_prof.get("num_ratings"),
                rmp_url=rmp_prof.get("profile_url"),
                department=department,
            )
            await services.instructor_repository.save(updated_instructor)
            matched += 1
            print(
                f"✓ Updated: {instructor_name} (Rating: {rmp_prof.get('overall_rating')}, Dept: {department})"
            )
        else:
            # Create new instructor if not found
            instructor_name = name
            if "ahn" in name.lower() and (
                "ted" in name.lower() or "tae" in name.lower()
            ):
                instructor_name = "Ted Ahn"

            new_instructor = Professor(
                id=None,
                name=instructor_name,
                rmp_rating=rmp_prof.get("overall_rating"),
                rmp_num_ratings=rmp_prof.get("num_ratings"),
                rmp_url=rmp_prof.get("profile_url"),
                department=dept_from_prof,
            )
            await services.instructor_repository.save(new_instructor)
            matched += 1
            print(
                f"✓ Created: {instructor_name} (Rating: {rmp_prof.get('overall_rating')}, Dept: {dept_from_prof})"
            )

    print(f"\nSummary:")
    print(f"  Updated/Created instructors: {matched}/{len(rmp_data)}")
    print(f"  Note: Individual RMP reviews load from JSON files automatically")


if __name__ == "__main__":
    asyncio.run(update_instructor_rmp_data())

