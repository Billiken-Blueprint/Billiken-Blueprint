from fastapi import APIRouter
from fastapi.routing import APIRoute

from billiken_blueprint.dependencies import CourseRepo


router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("")
async def list_courses(course_repo: CourseRepo):
    courses = await course_repo.get_all()
    return [
        dict(
            id=course.id,
            courseCode=f"{course.major_code} {course.course_number}",
        )
        for course in courses
    ]
