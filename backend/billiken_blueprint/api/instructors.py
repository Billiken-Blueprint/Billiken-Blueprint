from fastapi import APIRouter, HTTPException, status
from typing import Optional

from billiken_blueprint.dependencies import InstructorRepo, RmpReviewRepo


router = APIRouter(prefix="/instructors", tags=["instructors"])


@router.get("")
async def list_instructors(instructor_repo: InstructorRepo):
    instructors = await instructor_repo.get_all()
    return [
        {
            "id": instructor.id,
            "name": instructor.name,
            "rmpRating": instructor.rmp_rating,
            "rmpNumRatings": instructor.rmp_num_ratings,
            "rmpUrl": instructor.rmp_url,
            "department": instructor.department,
        }
        for instructor in instructors
    ]


@router.get("/{instructor_id}/reviews")
async def get_instructor_reviews(
    instructor_id: int,
    instructor_repo: InstructorRepo,
    rmp_review_repo: RmpReviewRepo,
):
    """Get all RMP reviews for a specific instructor."""
    # Verify instructor exists
    instructor = await instructor_repo.get_by_id(instructor_id)
    if not instructor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instructor with id {instructor_id} not found",
        )
    
    # Get reviews
    reviews = await rmp_review_repo.get_by_instructor_id(instructor_id)
    
    return [
        {
            "id": review.id,
            "instructorId": review.instructor_id,
            "course": review.course,
            "quality": review.quality,
            "difficulty": review.difficulty,
            "comment": review.comment,
            "wouldTakeAgain": review.would_take_again,
            "grade": review.grade,
            "attendance": review.attendance,
            "tags": review.tags,
            "reviewDate": review.review_date.isoformat() if review.review_date else None,
        }
        for review in reviews
    ]
