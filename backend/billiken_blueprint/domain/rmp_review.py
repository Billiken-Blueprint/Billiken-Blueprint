from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class RmpReview:
    id: Optional[int]
    instructor_id: int
    course: Optional[str]  # Course code/name from RMP (kept for backward compatibility)
    quality: float  # Rating 1-5
    difficulty: Optional[float]  # Difficulty 1-5
    comment: str
    would_take_again: Optional[bool]
    grade: Optional[str]
    attendance: Optional[str]
    tags: list[str]
    review_date: Optional[datetime]
    course_id: Optional[int] = None  # Foreign key to courses table

