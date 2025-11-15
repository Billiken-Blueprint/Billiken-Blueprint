from dataclasses import dataclass
import numbers
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc

from billiken_blueprint.dependencies import (
    AuthPayload,
    AuthToken,
    OptionalAuthPayload,
    IdentityUserRepo,
    InstructorRepo,
    RatingRepo,
    CourseRepo,
    StudentRepo,
    StudentRepo,
)
from billiken_blueprint.domain import instructor
from billiken_blueprint.domain.rating import Rating
from billiken_blueprint.identity.token_payload import TokenPayload


router = APIRouter(prefix="/ratings", tags=["ratings"])


@router.get("")
async def list_ratings(
    rating_repo: RatingRepo,
    instructor_repo: InstructorRepo,
    course_repo: CourseRepo,
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
        ))
    
    # Add RMP ratings
    if instructor_id:
        # If filtering by specific instructor, add their RMP rating
        instructor = await instructor_repo.get_by_id(instructor_id)
        if instructor and instructor.rmp_rating is not None:
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
    else:
        # If no instructor filter, show RMP ratings for all instructors that have them
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
    course_id: Optional[int] = None


@router.post("")
async def create_rating(
    rating_repo: RatingRepo,
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

    rating = Rating(
        id=None,
        course_id=body.course_id,
        professor_id=body.instructor_id,
        student_id=student_id,
        rating_value=body.rating,
        description=body.description,
    )
    new_rating = await rating_repo.save(rating)

    return {
        "id": new_rating.id,
        "instructorId": new_rating.professor_id,
        "courseId": new_rating.course_id,
        "rating": new_rating.rating_value,
        "description": new_rating.description,
    }
