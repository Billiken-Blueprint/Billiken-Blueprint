from dataclasses import dataclass


@dataclass
class Course:
    id: int
    major: str
    course_number: str
    course_code: str
    credits: int
