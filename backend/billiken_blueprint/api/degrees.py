from fastapi import APIRouter

from billiken_blueprint.dependencies import DegreeRepo


router = APIRouter(prefix="/degrees", tags=["degrees"])


@router.get("")
async def get_degrees(degree_repo: DegreeRepo):
    result = degree_repo.get_all()
    return [
        dict(major=deg.major, degreeType=deg.degree_type, college=deg.college)
        for deg in result
    ]
