from fastapi import APIRouter

router = APIRouter(prefix="/supported-majors", tags=["supported-majors"])


@router.get('')
def get_supported_majors():
    return ["CSCI B.A."]
