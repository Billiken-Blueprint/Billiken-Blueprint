from fastapi import APIRouter
from fastapi.routing import APIRoute

from billiken_blueprint.dependencies import CourseRepo
from billiken_blueprint.domain.course import Course


router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("/")
async def list_courses(course_repo: CourseRepo):
    courses = await course_repo.get_all()
    return [
        dict(id=course.id, course_code=course.course_code, title=course.title)
        for course in courses
    ]
