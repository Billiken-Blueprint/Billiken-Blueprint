from fastapi import APIRouter

from billiken_blueprint.dependencies import InstructorRepo


router = APIRouter(prefix="/instructors", tags=["instructors"])


@router.get("")
async def list_instructors(instructor_repo: InstructorRepo):
    instructors = await instructor_repo.get_all()
    return [dict(id=instructor.id, name=instructor.name) for instructor in instructors]
