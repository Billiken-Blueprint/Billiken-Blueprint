from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from click import Option


@dataclass
class Rating:
    id: Optional[int]
    course_id: Optional[int]
    professor_id: Optional[int]
    student_id: int
    rating_value: float
    description: str
    created_at: Optional[datetime] = None
    difficulty: Optional[float] = None  # Difficulty 1-5
    would_take_again: Optional[bool] = None
    grade: Optional[str] = None
    attendance: Optional[str] = None
