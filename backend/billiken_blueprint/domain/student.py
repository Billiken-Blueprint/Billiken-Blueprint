from calendar import c
from dataclasses import dataclass
from typing import Optional

from click import Option

from billiken_blueprint.domain.course import Course
from billiken_blueprint.domain.degree import Degree


@dataclass
class Student:
    id: Optional[int]
    name: str
    degree_ids: list[int]
    major_code: str
    degree_type: str
    college: str
    graduation_year: int
    completed_course_ids: list[int]
