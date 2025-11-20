from sys import prefix

from fastapi import APIRouter

from billiken_blueprint.dependencies import AuthPayload, DegreeRequirementsRepo


router = APIRouter(prefix="/degree-requirements", tags=["degree-requirements"])


@router.get("")
async def get_degree_requirements(auth: AuthPayload, reqs_repo: DegreeRequirementsRepo):
    return {}
