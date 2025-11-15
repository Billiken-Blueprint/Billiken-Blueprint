from dataclasses import dataclass
import numbers
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc

from billiken_blueprint.dependencies import (
    AuthPayload,
    AuthToken,
    IdentityUserRepo,
    RatingRepo,
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
    token_payload: AuthPayload,
    identity_repo: IdentityUserRepo,
    instructor_id: Optional[int] = None,
    course_id: Optional[int] = None,
):
    user_identity = await identity_repo.get_by_id(int(token_payload.sub))
    student_id = None
    if not user_identity or not user_identity.student_id:
        student_id = None
    else:
        student_id = user_identity.student_id

    ratings = await rating_repo.get_all(
        instructor_id=instructor_id, course_id=course_id
    )
    return [
        dict(
            id=rating.id,
            instructorId=rating.professor_id,
            courseId=rating.course_id,
            rating=rating.rating_value,
            canEdit=(student_id == rating.student_id),
            description=rating.description,
        )
        for rating in ratings
    ]


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
