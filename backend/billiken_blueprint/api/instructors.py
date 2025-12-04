from fastapi import APIRouter, HTTPException, status
from typing import Optional

from billiken_blueprint.dependencies import InstructorRepo, RmpReviewRepo, RatingRepo, CourseRepo, OptionalAuthPayload, IdentityUserRepo


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
    rating_repo: RatingRepo,
    course_repo: CourseRepo,
    token_payload: OptionalAuthPayload,
    identity_repo: IdentityUserRepo,
):
    """Get all reviews (RMP and user-generated) for a specific instructor."""
    # Verify instructor exists
    instructor = await instructor_repo.get_by_id(instructor_id)
    if not instructor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instructor with id {instructor_id} not found",
        )
    
    # Get current user's student ID if authenticated
    student_id = None
    if token_payload:
        user_identity = await identity_repo.get_by_id(int(token_payload.sub))
        if user_identity and user_identity.student_id:
            student_id = user_identity.student_id
    
    result = []
    
    # Get RMP reviews
    rmp_reviews = await rmp_review_repo.get_by_instructor_id(instructor_id)
    for review in rmp_reviews:
        course_code = None
        course_name = None
        if review.course_id:
            course = await course_repo.get_by_id(review.course_id)
            if course:
                course_code = f"{course.major_code} {course.course_number}"
                # Course domain object doesn't have title, use course_code as name
                course_name = course_code
        
        result.append({
            "id": review.id,
            "type": "rmp",
            "instructorId": review.instructor_id,
            "course": review.course,
            "courseCode": course_code,
            "courseName": course_name,
            "courseId": review.course_id,
            "quality": review.quality,
            "difficulty": review.difficulty,
            "comment": review.comment,
            "wouldTakeAgain": review.would_take_again,
            "grade": review.grade,
            "attendance": review.attendance,
            "tags": review.tags,
            "reviewDate": review.review_date.isoformat() if review.review_date else None,
        })
    
    # Get user-generated ratings (Billiken Blueprint)
    user_ratings = await rating_repo.get_all(instructor_id=instructor_id)
    for rating in user_ratings:
        course_code = None
        course_name = None
        if rating.course_id:
            course = await course_repo.get_by_id(rating.course_id)
            if course:
                course_code = f"{course.major_code} {course.course_number}"
                # Course domain object doesn't have title, use course_code as name
                course_name = course_code
        
        result.append({
            "id": rating.id,
            "type": "billiken_blueprint",
            "instructorId": rating.professor_id,
            "courseCode": course_code,
            "courseName": course_name,
            "quality": rating.rating_value,
            "comment": rating.description,
            "reviewDate": rating.created_at.isoformat() if rating.created_at else None,
            "difficulty": rating.difficulty,
            "wouldTakeAgain": rating.would_take_again,
            "grade": rating.grade,
            "attendance": rating.attendance,
            "canDelete": (student_id is not None and rating.student_id == student_id),
        })
    
    return result
