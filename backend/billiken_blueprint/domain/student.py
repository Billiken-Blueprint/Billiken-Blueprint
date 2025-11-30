from calendar import c
from dataclasses import dataclass
from typing import Optional


@dataclass
class Student:
    id: Optional[int]
    name: str
    degree_id: int
    graduation_year: int
    completed_course_ids: list[int]
