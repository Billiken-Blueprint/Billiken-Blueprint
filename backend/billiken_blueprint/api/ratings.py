from dataclasses import dataclass
import numbers
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc

from billiken_blueprint.dependencies import (
    AuthPayload,
    AuthToken,
    RmpReviewRepo,
    OptionalAuthPayload,
    IdentityUserRepo,
    InstructorRepo,
    RatingRepo,
    CourseRepo,
    StudentRepo,
    StudentRepo,
)
from billiken_blueprint.domain import instructor
from billiken_blueprint.domain.instructor import Professor
from billiken_blueprint.domain.rating import Rating
from billiken_blueprint.identity.token_payload import TokenPayload


router = APIRouter(prefix="/ratings", tags=["ratings"])


@router.get("")
async def list_ratings(
    rating_repo: RatingRepo,
    instructor_repo: InstructorRepo,
    course_repo: CourseRepo,
    rmp_review_repo: RmpReviewRepo,
    token_payload: OptionalAuthPayload,
    identity_repo: IdentityUserRepo,
    instructor_id: Optional[int] = None,
    course_id: Optional[int] = None,
):
    student_id = None
    if token_payload:
        user_identity = await identity_repo.get_by_id(int(token_payload.sub))
        if user_identity and user_identity.student_id:
            student_id = user_identity.student_id

    ratings = await rating_repo.get_all(
        instructor_id=instructor_id, course_id=course_id
    )
    
    # Get course info if filtering by course
    target_course_code = None
    if course_id:
        db_course = await course_repo.get_by_id(course_id)
        if db_course:
            course = db_course.to_course()
            target_course_code = course.course_code
    
    # Build result with instructor and course names
    result = []
    for rating in ratings:
        instructor_name = None
        course_code = None
        course_name = None
        
        if rating.professor_id:
            instructor = await instructor_repo.get_by_id(rating.professor_id)
            if instructor:
                instructor_name = instructor.name
        
        if rating.course_id:
            db_course = await course_repo.get_by_id(rating.course_id)
            if db_course:
                course = db_course.to_course()
                course_code = course.course_code
                course_name = course.title
        
        result.append(dict(
            id=rating.id,
            instructorId=rating.professor_id,
            courseId=rating.course_id,
            rating=rating.rating_value,
            canEdit=(student_id == rating.student_id),
            description=rating.description,
            isRmpRating=False,
            instructorName=instructor_name,
            courseCode=course_code,
            courseName=course_name,
            createdAt=rating.created_at.isoformat() if rating.created_at else None,
            difficulty=rating.difficulty,
            wouldTakeAgain=rating.would_take_again,
            grade=rating.grade,
            attendance=rating.attendance,
        ))
    
    # Helper function to normalize course codes for matching
    def normalize_course_code(course_code: str) -> str:
        """Normalize course code by removing spaces and converting to uppercase."""
        if not course_code:
            return ""
        # Remove all spaces and convert to uppercase
        return course_code.replace(" ", "").replace("-", "").upper()
    
    # Helper function to check if a course code matches
    def course_code_matches(review_course: Optional[str], target: str) -> bool:
        """Check if a review's course field matches the target course code."""
        if not review_course or not target:
            return False
        normalized_review = normalize_course_code(review_course)
        # Check if target is contained in review course (handles formats like "CSCI3100" or "CSCI 3100 - Algorithms")
        return target in normalized_review or normalized_review in target
    
    # Normalize target course code if filtering by course
    normalized_target = None
    if target_course_code:
        normalized_target = normalize_course_code(target_course_code)
    
    # Add RMP ratings
    if instructor_id:
        # If filtering by specific instructor, add their RMP rating
        instructor = await instructor_repo.get_by_id(instructor_id)
        if instructor and instructor.rmp_rating is not None:
            # If filtering by course, check if instructor has RMP reviews for that course
            include_rmp = True
            if course_id:
                # Check if instructor has any RMP reviews for this course using course_id (most reliable)
                rmp_reviews = await rmp_review_repo.get_by_instructor_id(instructor_id)
                if rmp_reviews:
                    # Check if any review has matching course_id
                    course_matched = any(
                        review.course_id == course_id for review in rmp_reviews
                    )
                    # If no course_id match, fall back to course string matching
                    if not course_matched and normalized_target:
                        course_matched = any(
                            course_code_matches(review.course, normalized_target)
                            for review in rmp_reviews
                        )
                    include_rmp = course_matched
                else:
                    # If no reviews but has RMP rating, don't include it when filtering by course
                    include_rmp = False
            elif normalized_target:
                # If filtering by course code string (no course_id), use string matching
                rmp_reviews = await rmp_review_repo.get_by_instructor_id(instructor_id)
                if rmp_reviews:
                    course_matched = any(
                        course_code_matches(review.course, normalized_target)
                        for review in rmp_reviews
                    )
                    include_rmp = course_matched
                else:
                    include_rmp = True
            
            if include_rmp:
                result.append(dict(
                    id=None,  # RMP ratings don't have database IDs
                    instructorId=instructor.id,
                    courseId=course_id if course_id else None,
                    rating=instructor.rmp_rating,
                    canEdit=False,
                    description=f"RateMyProfessor rating based on {instructor.rmp_num_ratings} reviews",
                    isRmpRating=True,
                    rmpUrl=instructor.rmp_url,
                    rmpNumRatings=instructor.rmp_num_ratings,
                    instructorName=instructor.name,
                    courseCode=target_course_code if target_course_code else None,
                    courseName=None,
                ))
    elif course_id and target_course_code:
        # If filtering by course but not instructor, find all instructors with RMP reviews for this course
        # Use course_id to directly query RMP reviews
        rmp_reviews_for_course = await rmp_review_repo.get_by_course_id(course_id)
        instructor_ids_with_reviews = set(review.instructor_id for review in rmp_reviews_for_course)
        
        for instructor_id in instructor_ids_with_reviews:
            instructor = await instructor_repo.get_by_id(instructor_id)
            if instructor and instructor.rmp_rating is not None:
                result.append(dict(
                    id=None,  # RMP ratings don't have database IDs
                    instructorId=instructor.id,
                    courseId=course_id,
                    rating=instructor.rmp_rating,
                    canEdit=False,
                    description=f"RateMyProfessor rating based on {instructor.rmp_num_ratings} reviews",
                    isRmpRating=True,
                    rmpUrl=instructor.rmp_url,
                    rmpNumRatings=instructor.rmp_num_ratings,
                    instructorName=instructor.name,
                    courseCode=target_course_code,
                    courseName=None,
                ))
    else:
        # If no filters, show RMP ratings for all instructors that have them
        all_instructors = await instructor_repo.get_all()
        for instructor in all_instructors:
            if instructor.rmp_rating is not None:
                result.append(dict(
                    id=None,  # RMP ratings don't have database IDs
                    instructorId=instructor.id,
                    courseId=None,
                    rating=instructor.rmp_rating,
                    canEdit=False,
                    description=f"RateMyProfessor rating based on {instructor.rmp_num_ratings} reviews",
                    isRmpRating=True,
                    rmpUrl=instructor.rmp_url,
                    rmpNumRatings=instructor.rmp_num_ratings,
                    instructorName=instructor.name,
                    courseCode=None,
                    courseName=None,
                ))
    
    return result


class CreateRatingBody(BaseModel):
    rating: int
    description: str
    instructor_id: Optional[int] = None
    instructor_name: Optional[str] = None  # For creating new instructors
    instructor_department: Optional[str] = None  # Department for new instructors
    course_id: Optional[int] = None
    difficulty: Optional[float] = None
    would_take_again: Optional[bool] = None
    grade: Optional[str] = None
    attendance: Optional[str] = None


@router.post("")
async def create_rating(
    rating_repo: RatingRepo,
    instructor_repo: InstructorRepo,
    identity_repo: IdentityUserRepo,
    token_payload: AuthPayload,
    body: CreateRatingBody,
):
    user_identity = await identity_repo.get_by_id(int(token_payload.sub))
    if not user_identity or not user_identity.student_id:
        raise HTTPException(
            status_code=400, detail="User does not have an associated student record."
        )
    student_id = user_identity.student_id

    # Handle instructor creation if instructor_name is provided but instructor_id is not
    professor_id = body.instructor_id
    if not professor_id and body.instructor_name:
        # Check if instructor already exists by name
        existing_instructor = await instructor_repo.get_by_name(body.instructor_name.strip())
        if existing_instructor:
            professor_id = existing_instructor.id
        else:
            # Create new instructor
            new_instructor = Professor(
                id=None,
                name=body.instructor_name.strip(),
                department=body.instructor_department if body.instructor_department else None,
            )
            saved_instructor = await instructor_repo.save(new_instructor)
            professor_id = saved_instructor.id

    if not professor_id:
        raise HTTPException(
            status_code=400, detail="Either instructor_id or instructor_name must be provided."
        )

    rating = Rating(
        id=None,
        course_id=body.course_id,
        professor_id=professor_id,
        student_id=student_id,
        rating_value=body.rating,
        description=body.description,
        difficulty=body.difficulty,
        would_take_again=body.would_take_again,
        grade=body.grade,
        attendance=body.attendance,
    )
    new_rating = await rating_repo.save(rating)

    return {
        "id": new_rating.id,
        "instructorId": new_rating.professor_id,
        "courseId": new_rating.course_id,
        "rating": new_rating.rating_value,
        "description": new_rating.description,
    }


@router.put("/{rating_id}")
async def update_rating(
    rating_id: int,
    rating_repo: RatingRepo,
    identity_repo: IdentityUserRepo,
    token_payload: AuthPayload,
    body: CreateRatingBody,
):
    """Update a rating. Only the creator can update their own rating."""
    user_identity = await identity_repo.get_by_id(int(token_payload.sub))
    if not user_identity or not user_identity.student_id:
        raise HTTPException(
            status_code=400, detail="User does not have an associated student record."
        )
    student_id = user_identity.student_id
    
    # Get the rating to verify ownership
    ratings = await rating_repo.get_all()
    existing_rating = next((r for r in ratings if r.id == rating_id), None)
    
    if not existing_rating:
        raise HTTPException(
            status_code=404, detail=f"Rating with id {rating_id} not found"
        )
    
    if existing_rating.student_id != student_id:
        raise HTTPException(
            status_code=403, detail="You can only update your own ratings"
        )
    
    # Update the rating - preserve existing course_id and professor_id if not provided
    updated_rating = Rating(
        id=rating_id,
        course_id=body.course_id if body.course_id is not None else existing_rating.course_id,
        professor_id=body.instructor_id if body.instructor_id is not None else existing_rating.professor_id,
        student_id=student_id,
        rating_value=body.rating,
        description=body.description,
        difficulty=body.difficulty if body.difficulty is not None else existing_rating.difficulty,
        would_take_again=body.would_take_again if body.would_take_again is not None else existing_rating.would_take_again,
        grade=body.grade if body.grade is not None else existing_rating.grade,
        attendance=body.attendance if body.attendance is not None else existing_rating.attendance,
        created_at=existing_rating.created_at,  # Preserve original creation time
    )
    
    saved_rating = await rating_repo.save(updated_rating)
    
    return {
        "id": saved_rating.id,
        "instructorId": saved_rating.professor_id,
        "courseId": saved_rating.course_id,
        "rating": saved_rating.rating_value,
        "description": saved_rating.description,
    }


@router.delete("/{rating_id}")
async def delete_rating(
    rating_id: int,
    rating_repo: RatingRepo,
    identity_repo: IdentityUserRepo,
    token_payload: AuthPayload,
):
    """Delete a rating. Only the creator can delete their own rating."""
    user_identity = await identity_repo.get_by_id(int(token_payload.sub))
    if not user_identity or not user_identity.student_id:
        raise HTTPException(
            status_code=400, detail="User does not have an associated student record."
        )
    student_id = user_identity.student_id
    
    # Get the rating to verify ownership
    ratings = await rating_repo.get_all()
    rating = next((r for r in ratings if r.id == rating_id), None)
    
    if not rating:
        raise HTTPException(
            status_code=404, detail=f"Rating with id {rating_id} not found"
        )
    
    if rating.student_id != student_id:
        raise HTTPException(
            status_code=403, detail="You can only delete your own ratings"
        )
    
    await rating_repo.delete(rating_id)
    return {"message": "Rating deleted successfully"}
