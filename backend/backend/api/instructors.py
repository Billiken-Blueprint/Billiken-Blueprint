from fastapi import APIRouter

router = APIRouter(prefix="/api/instructors", tags=["instructors"])


@router.get("")
async def get_instructors():
    """Get all instructors"""
    # TODO: Replace with actual database query
    return [
        {"id": 1, "name": "Dr. Smith"},
        {"id": 2, "name": "Dr. Johnson"},
        {"id": 3, "name": "Dr. Williams"},
        {"id": 4, "name": "Dr. Brown"},
        {"id": 5, "name": "Dr. Davis"},
    ]


@router.get("/{instructor_id}")
async def get_instructor(instructor_id: int):
    """Get a specific instructor by ID"""
    # TODO: Replace with actual database query
    return {"id": instructor_id, "name": f"Dr. Instructor {instructor_id}"}
