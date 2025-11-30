from fastapi import APIRouter

from billiken_blueprint.dependencies import DegreeRepo


router = APIRouter(prefix="/degrees", tags=["degrees"])


@router.get("")
async def get_degrees(degree_repo: DegreeRepo):
    result = await degree_repo.get_all()
    return [
        dict(
            id=deg.id,
            name=deg.name,
            major=deg.degree_works_major_code,
            degreeType=deg.degree_works_degree_type,
            college=deg.degree_works_college_code,
        )
        for deg in result
    ]
