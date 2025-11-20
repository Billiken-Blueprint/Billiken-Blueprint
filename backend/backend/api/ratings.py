from typing import Optional
from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/ratings", tags=["ratings"])


@router.get("")
async def get_ratings(
    instructor_id: Optional[str] = Query(None),
    course_id: Optional[str] = Query(None)
):
    """Get ratings filtered by instructor and/or course"""
    # TODO: Replace with actual database query
    all_ratings = [
        {
            "id": 1,
            "instructorId": 1,
            "courseId": 1,
            "rating": 5,
            "description": "Excellent professor! Very clear explanations and helpful during office hours.",
            "canEdit": False,
            "instructorName": "Dr. Smith",
            "courseCode": "CSCI 1300",
            "courseName": "Introduction to Computer Science",
            "createdAt": "2024-11-15T10:30:00Z"
        },
        {
            "id": 2,
            "instructorId": 1,
            "courseId": 2,
            "rating": 4,
            "description": "Great teacher, but the assignments can be challenging.",
            "canEdit": False,
            "instructorName": "Dr. Smith",
            "courseCode": "CSCI 2100",
            "courseName": "Data Structures",
            "createdAt": "2024-11-10T14:20:00Z"
        },
        {
            "id": 3,
            "instructorId": 2,
            "courseId": 1,
            "rating": 3,
            "description": "Decent course, but could use more examples.",
            "canEdit": False,
            "instructorName": "Dr. Johnson",
            "courseCode": "CSCI 1300",
            "courseName": "Introduction to Computer Science",
            "createdAt": "2024-11-05T09:15:00Z"
        },
    ]
    
    # Filter by instructor_id if provided
    if instructor_id:
        all_ratings = [r for r in all_ratings if str(r["instructorId"]) == instructor_id]
    
    # Filter by course_id if provided
    if course_id:
        all_ratings = [r for r in all_ratings if str(r["courseId"]) == course_id]
    
    return all_ratings


@router.post("")
async def create_rating(body: dict):
    """Create a new rating"""
    # TODO: Replace with actual database insert
    return {
        "id": 999,
        "instructorId": body.get("instructor_id"),
        "courseId": body.get("course_id"),
        "rating": body.get("rating"),
        "description": body.get("description"),
        "canEdit": True,
        "createdAt": "2024-11-19T12:00:00Z"
    }
