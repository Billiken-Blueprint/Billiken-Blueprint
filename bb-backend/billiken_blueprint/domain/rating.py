from dataclasses import dataclass
from typing import Optional

from click import Option


@dataclass
class Rating:
    id: Optional[int]
    course_id: Optional[int]
    professor_id: Optional[int]
    student_id: int
    rating_value: float
    description: str
