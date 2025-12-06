from fastapi import APIRouter, Query
from fastapi.routing import APIRoute

from billiken_blueprint.dependencies import CourseRepo, CourseDescriptionsCollection
from billiken_blueprint.use_cases.get_courses_from_user_query import get_courses_from_user_query


router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("/search")
async def search_courses(
    query: str,
    collection: CourseDescriptionsCollection,
):
    results = get_courses_from_user_query(query, collection)
    return results

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
