"""Import RateMyProfessor ratings and reviews from JSON file and match with instructors."""

import asyncio
import json
import re
from pathlib import Path
from datetime import datetime
from pathlib import Path
import sys

# Add the parent directory to the path so we can import billiken_blueprint
sys.path.insert(0, str(Path(__file__).parent.parent))

from billiken_blueprint import services
from billiken_blueprint.domain.instructor import Professor
from billiken_blueprint.domain.ratings.rmp_review import RmpReview


async def import_rmp_ratings():
    """Import RMP ratings and reviews from JSON files and update instructors."""
    script_dir = Path(__file__).parent

    # Define possible paths for CS professors (prioritize files with reviews)
    cs_possible_paths = [
        Path("data_dumps/cs_professors_with_reviews.json"),
        Path("data_dumps/cs_professors.json"),
        script_dir / "cs_professors_with_reviews.json",
        script_dir / "cs_professors.json",
        script_dir.parent
        / "ratemyprofessor-scraping"
        / "cs_professors_with_reviews.json",
        script_dir.parent / "ratemyprofessor-scraping" / "cs_professors.json",
        Path("/app/cs_professors_with_reviews.json"),
        Path("/app/cs_professors.json"),
    ]

    # Define possible paths for Math professors
    math_possible_paths = [
        Path("data_dumps/math_professors_with_reviews.json"),
        Path("data_dumps/math_professors.json"),
        script_dir / "math_professors_with_reviews.json",
        script_dir / "math_professors.json",
        script_dir.parent
        / "ratemyprofessor-scraping"
        / "math_professors_with_reviews.json",
        script_dir.parent / "ratemyprofessor-scraping" / "math_professors.json",
        Path("/app/math_professors_with_reviews.json"),
        Path("/app/math_professors.json"),
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

    # Load RMP data with department information
    rmp_data = []

    if cs_file and cs_file.exists():
        print(f"Loading CS RMP data from: {cs_file}")
        with open(cs_file, "r") as f:
            cs_data = json.load(f)
            # Add department info to CS professors
            for prof in cs_data:
                prof["_department"] = "CSCI"  # Mark as CSCI department
            rmp_data.extend(cs_data)
            print(f"Loaded {len(cs_data)} CS professor records")
    else:
        print("CS professors file not found, skipping...")

    if math_file and math_file.exists():
        print(f"Loading Math RMP data from: {math_file}")
        with open(math_file, "r") as f:
            math_data = json.load(f)
            # Add department info to Math professors
            for prof in math_data:
                prof["_department"] = "MATH"  # Mark as MATH department
            rmp_data.extend(math_data)
            print(f"Loaded {len(math_data)} Math professor records")
    else:
        print("Math professors file not found, skipping...")

    if not rmp_data:
        print("No RMP data found in any of the expected locations")
        return

    print(f"Total RMP professor records: {len(rmp_data)}")

    # Get all existing instructors
    existing_instructors = await services.instructor_repository.get_all()
    instructor_by_name = {
        instructor.name.lower(): instructor for instructor in existing_instructors
    }

    matched = 0
    not_matched = []
    total_reviews = 0

    for rmp_prof in rmp_data:
        name = rmp_prof.get("name", "").strip()
        if not name:
            continue

        # Debug: check if _department is set
        dept_from_prof = rmp_prof.get("_department")

        # Try exact match first
        instructor = instructor_by_name.get(name.lower())

        # If no exact match, try partial matches (handle variations like "Dr. Name" vs "Name", "Greg" vs "Gregory")
        if not instructor:
            # Try matching by last name or removing middle names/initials
            rmp_name_parts = name.lower().split()
            for existing_name, existing_instructor in instructor_by_name.items():
                existing_parts = existing_name.split()
                # Match if last names match
                if (
                    rmp_name_parts
                    and existing_parts
                    and rmp_name_parts[-1] == existing_parts[-1]
                ):  # Last name match
                    # Also check if first names are similar (e.g., "Greg" vs "Gregory")
                    rmp_first = rmp_name_parts[0] if rmp_name_parts else ""
                    existing_first = existing_parts[0] if existing_parts else ""
                    # Match if first names are the same or one is a prefix of the other (Greg/Gregory, Jim/James)
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
                        # Update name if RMP has a better version (e.g., "Tae-Hyuk (Ted) Ahn" -> "Ted Ahn")
                        if "ted" in name.lower() and "ted" not in existing_name.lower():
                            # Update to use Ted if RMP has it
                            updated_instructor = Professor(
                                id=existing_instructor.id,
                                name=(
                                    "Ted Ahn"
                                    if "ahn" in name.lower()
                                    else existing_instructor.name
                                ),
                                rmp_rating=rmp_prof.get("overall_rating"),
                                rmp_num_ratings=rmp_prof.get("num_ratings"),
                                rmp_url=rmp_prof.get("profile_url"),
                                department=rmp_prof.get("_department")
                                or existing_instructor.department,
                            )
                            await services.instructor_repository.save(
                                updated_instructor
                            )
                        break
                # Also try substring matching
                if name.lower() in existing_name or existing_name in name.lower():
                    instructor = existing_instructor
                    break

        if instructor:
            # Update instructor with RMP aggregated data
            # Use the department from RMP data, or keep existing if RMP doesn't have one
            department = dept_from_prof or instructor.department
            if not department and dept_from_prof:
                department = dept_from_prof  # Ensure we use _department if it exists

            # Normalize name: always use "Ted Ahn" instead of "Tae Ahn" or "Tae-Hyuk (Ted) Ahn"
            instructor_name = instructor.name
            if "ahn" in name.lower() and (
                "ted" in name.lower() or "tae" in name.lower()
            ):
                instructor_name = "Ted Ahn"
            elif "ahn" in instructor.name.lower() and (
                "tae" in instructor.name.lower()
                and "ted" not in instructor.name.lower()
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
                f"✓ Matched: {name} -> {instructor_name} (Rating: {rmp_prof.get('overall_rating')}, Dept: {department})"
            )
        else:
            # Create new instructor if not found (for math professors or others not in CSCI courses)
            # Normalize name: always use "Ted Ahn" instead of "Tae Ahn" or "Tae-Hyuk (Ted) Ahn"
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
                department=rmp_prof.get("_department"),
            )
            instructor = await services.instructor_repository.save(new_instructor)
            matched += 1
            print(
                f"✓ Created new instructor: {instructor_name} (Rating: {rmp_prof.get('overall_rating')}, Dept: {rmp_prof.get('_department')})"
            )

        if instructor:

            # Import individual reviews if available (skip if table doesn't exist)
            reviews = rmp_prof.get("reviews", [])
            if reviews:
                try:
                    rmp_reviews = []
                    for review_data in reviews:
                        # Parse date if available
                        review_date = None
                        if review_data.get("date"):
                            try:
                                # Try to parse date string if it's in a standard format
                                review_date = datetime.fromisoformat(
                                    str(review_data["date"]).replace("Z", "+00:00")
                                )
                            except (ValueError, TypeError):
                                pass

                        # Try to match course code from RMP review to database course
                        course_id = None
                        course_string = review_data.get("course")
                        if course_string:
                            # Extract course code pattern (e.g., "CSCI 3100" or "CSCI3100")
                            # Match patterns like "CSCI 3100", "CSCI3100", "MATH 1200", etc.
                            course_code_match = re.search(
                                r"([A-Z]+)\s*(\d{4})", course_string.upper()
                            )
                            if course_code_match:
                                department = course_code_match.group(1)
                                number = course_code_match.group(2)
                                potential_course_code = f"{department} {number}"

                                # Try to find matching course in database
                                db_course = (
                                    await services.course_repository.get_by_code(
                                        potential_course_code
                                    )
                                )
                                if db_course:
                                    course_id = db_course.id

                        rmp_review = RmpReview(
                            id=None,  # Auto-increment
                            instructor_id=instructor.id,
                            course=course_string,
                            quality=review_data.get("quality", 0.0),
                            difficulty=review_data.get("difficulty"),
                            comment=review_data.get("comment", ""),
                            would_take_again=review_data.get("would_take_again"),
                            grade=review_data.get("grade"),
                            attendance=review_data.get("attendance"),
                            tags=review_data.get("tags", []) or [],
                            review_date=review_date,
                            course_id=course_id,
                        )
                        rmp_reviews.append(rmp_review)

                    # Delete existing reviews for this instructor and save new ones
                    await services.rmp_review_repository.delete_by_instructor_id(
                        instructor.id
                    )
                    if rmp_reviews:
                        await services.rmp_review_repository.save_many(rmp_reviews)
                        total_reviews += len(rmp_reviews)
                        print(
                            f"  → Imported {len(rmp_reviews)} reviews for {instructor.name}"
                        )
                except Exception as e:
                    # Skip reviews import if table doesn't exist or other error
                    print(
                        f"  → Skipped reviews import for {instructor.name} (table may not exist)"
                    )
        else:
            not_matched.append(name)
            print(f"✗ No match found and could not create: {name}")

    print(f"\nSummary:")
    print(f"  Matched instructors: {matched}/{len(rmp_data)}")
    print(f"  Total reviews imported: {total_reviews}")
    print(f"  Not matched: {len(not_matched)}")
    if not_matched:
        print(f"\nUnmatched professors:")
        for name in not_matched[:10]:  # Show first 10
            print(f"  - {name}")


if __name__ == "__main__":
    asyncio.run(import_rmp_ratings())
