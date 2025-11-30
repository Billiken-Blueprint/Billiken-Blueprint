"""Update existing RMP reviews to set course_id by matching course codes."""

import asyncio
import re
from billiken_blueprint import services


async def update_rmp_review_course_ids():
    """Update course_id for existing RMP reviews by matching course codes."""
    print("Starting to update RMP review course_ids...")

    # Get all courses
    all_courses = await services.course_repository.get_all()
    course_map = {}  # Map normalized course code to course object
    for course in all_courses:
        normalized = course.course_code.replace(" ", "").replace("-", "").upper()
        course_map[normalized] = course

    print(f"Loaded {len(course_map)} courses from database")

    # Get all instructors
    all_instructors = await services.instructor_repository.get_all()
    print(f"Processing {len(all_instructors)} instructors...")

    total_updated = 0
    total_reviews = 0

    for instructor in all_instructors:
        # Get all RMP reviews for this instructor
        rmp_reviews = await services.rmp_review_repository.get_by_instructor_id(
            instructor.id
        )
        total_reviews += len(rmp_reviews)

        updated_reviews = []
        for review in rmp_reviews:
            # Skip if already has course_id
            if review.course_id:
                continue

            # Try to match course code from review.course string
            if review.course:
                # Extract course code pattern (e.g., "CSCI 3100" or "CSCI3100")
                course_code_match = re.search(
                    r"([A-Z]+)\s*(\d{4})", review.course.upper()
                )
                if course_code_match:
                    department = course_code_match.group(1)
                    number = course_code_match.group(2)
                    potential_course_code = f"{department} {number}"

                    # Try to find matching course in database
                    db_course = await services.course_repository.get_by_code(
                        potential_course_code
                    )
                    if db_course:
                        # Update review with course_id
                        from billiken_blueprint.domain.ratings.rmp_review import (
                            RmpReview,
                        )

                        updated_review = RmpReview(
                            id=review.id,
                            instructor_id=review.instructor_id,
                            course=review.course,
                            course_id=db_course.id,
                            quality=review.quality,
                            difficulty=review.difficulty,
                            comment=review.comment,
                            would_take_again=review.would_take_again,
                            grade=review.grade,
                            attendance=review.attendance,
                            tags=review.tags,
                            review_date=review.review_date,
                        )
                        updated_reviews.append(updated_review)

        # Save updated reviews
        if updated_reviews:
            for updated_review in updated_reviews:
                await services.rmp_review_repository.save(updated_review)
            total_updated += len(updated_reviews)
            print(f"  Updated {len(updated_reviews)} reviews for {instructor.name}")

    print(f"\nSummary:")
    print(f"  Total RMP reviews processed: {total_reviews}")
    print(f"  Reviews updated with course_id: {total_updated}")
    print(f"  Reviews already had course_id: {total_reviews - total_updated}")


if __name__ == "__main__":
    asyncio.run(update_rmp_review_course_ids())
