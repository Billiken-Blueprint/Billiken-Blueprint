from dataclasses import dataclass
from typing import Optional


@dataclass
class Course:
    id: Optional[int]
    major: str
    title: str
    course_number: str
    course_code: str
    description: str
