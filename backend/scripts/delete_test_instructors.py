"""Script to delete test instructors from the database."""
import asyncio
from sqlalchemy import delete, select
from billiken_blueprint import services
from billiken_blueprint.repositories.instructor_repository import DBInstructor
from billiken_blueprint.repositories.rating_repository import DBRating
from billiken_blueprint.repositories.rmp_review_repository import DBRmpReview
from billiken_blueprint.repositories.course_section_repository import instructor_sections_association

async def delete_test_instructors():
    """Delete test instructors by name."""
    test_names = ["Testing", "testin1", "testing1", "test2", "test3"]
    
    async with services.async_sessionmaker() as session:
        # First, find the instructor IDs
        from sqlalchemy import select
        stmt = select(DBInstructor).where(DBInstructor.name.in_(test_names))
        result = await session.execute(stmt)
        instructors = result.scalars().all()
        
        if not instructors:
            print("No test instructors found to delete.")
            return
        
        instructor_ids = [inst.id for inst in instructors]
        print(f"Found {len(instructor_ids)} test instructors to delete: {[inst.name for inst in instructors]}")
        
        # Delete ratings associated with these instructors
        delete_ratings_stmt = delete(DBRating).where(DBRating.professor_id.in_(instructor_ids))
        ratings_result = await session.execute(delete_ratings_stmt)
        print(f"Deleted {ratings_result.rowcount} ratings")
        
        # Delete RMP reviews associated with these instructors
        delete_rmp_stmt = delete(DBRmpReview).where(DBRmpReview.instructor_id.in_(instructor_ids))
        rmp_result = await session.execute(delete_rmp_stmt)
        print(f"Deleted {rmp_result.rowcount} RMP reviews")
        
        # Delete instructor-section associations
        delete_assoc_stmt = delete(instructor_sections_association).where(
            instructor_sections_association.c.instructor_id.in_(instructor_ids)
        )
        assoc_result = await session.execute(delete_assoc_stmt)
        print(f"Deleted {assoc_result.rowcount} instructor-section associations")
        
        # Finally, delete the instructors themselves
        delete_instructors_stmt = delete(DBInstructor).where(DBInstructor.id.in_(instructor_ids))
        instructors_result = await session.execute(delete_instructors_stmt)
        print(f"Deleted {instructors_result.rowcount} instructors")
        
        await session.commit()
        print("Successfully deleted all test instructors and their associated data.")

if __name__ == "__main__":
    asyncio.run(delete_test_instructors())

