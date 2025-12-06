from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from billiken_blueprint.dependencies import (
    CourseRepo,
    CurrentIdentity,
    CurrentStudent,
    IdentityUserRepo,
    StudentRepo,
)
from billiken_blueprint.domain.student import Student, TimeSlot


router = APIRouter(prefix="/user_info", tags=["user_info"])

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


class TimeSlotBody(BaseModel):
    day: int
    start: str  # HHMM format
    end: str    # HHMM format


class UserInfoBody(BaseModel):
    name: str
    graduation_year: int
    completed_course_ids: list[int]
    unavailability_times: list[TimeSlotBody]
    avoid_times: list[TimeSlotBody]
    degree_id: int


@router.post("")
async def set_user_info(
    identity: CurrentIdentity,
    user_info: UserInfoBody,
    identity_user_repo: IdentityUserRepo,
    student_repo: StudentRepo,
):
    student = Student(
        id=identity.student_id,
        name=user_info.name,
        completed_course_ids=user_info.completed_course_ids,
        desired_course_ids=[],
        unavailability_times=[TimeSlot(day=ts.day, start=ts.start, end=ts.end) for ts in user_info.unavailability_times],
        avoid_times=[TimeSlot(day=ts.day, start=ts.start, end=ts.end) for ts in user_info.avoid_times],
        graduation_year=user_info.graduation_year,
        degree_id=user_info.degree_id,
    )
    student = await student_repo.save(student)

    identity.student_id = student.id
    await identity_user_repo.save(identity)


@router.get("")
async def get_user_info(student: CurrentStudent, course_repo: CourseRepo):
    saved_courses = [
        await course_repo.get_by_id(id) for id in student.completed_course_ids
    ]
    saved_course_codes = [
        f"{c.major_code} {c.course_number}" for c in saved_courses if c is not None
    ]

    return dict(
        name=student.name,
        completedCourseIds=student.completed_course_ids,
        desiredCourseIds=student.desired_course_ids,
        unavailabilityTimes=[{"day": ts.day, "start": ts.start, "end": ts.end} for ts in student.unavailability_times],
        avoidTimes=[{"day": ts.day, "start": ts.start, "end": ts.end} for ts in student.avoid_times],
        savedCourseCodes=saved_course_codes,
        graduationYear=student.graduation_year,
        degreeId=student.degree_id,
    )
