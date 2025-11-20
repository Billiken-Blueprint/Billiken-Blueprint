from fastapi import APIRouter

router = APIRouter(prefix="/api/courses", tags=["courses"])


@router.get("")
async def get_courses():
    """Get all courses"""
    # TODO: Replace with actual database query
    return [
        {"id": 1, "courseCode": "CSCI 1300", "title": "Introduction to Computer Science"},
        {"id": 2, "courseCode": "CSCI 2100", "title": "Data Structures"},
        {"id": 3, "courseCode": "CSCI 2300", "title": "Algorithms"},
        {"id": 4, "courseCode": "MATH 1200", "title": "Calculus I"},
        {"id": 5, "courseCode": "MATH 1210", "title": "Calculus II"},
    ]


@router.get("/{course_id}")
async def get_course(course_id: int):
    """Get a specific course by ID"""
    # TODO: Replace with actual database query
    return {"id": course_id, "courseCode": f"CSCI {course_id}000", "title": f"Course {course_id}"}
