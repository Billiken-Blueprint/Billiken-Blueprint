from dataclasses import dataclass
from os import major
from typing import Optional

from click import Option

from billiken_blueprint.domain.course_attribute import CourseAttribute


@dataclass
class Course:
    id: Optional[int]
    course_code: str
    major: str
    title: str
    course_number: str
    description: str


@dataclass
class MinimalCourse:
    id: int | None
    major_code: str
    course_number: str
    attributes: list[CourseAttribute]

    def __hash__(self) -> int:
        return self.major_code.__hash__() + self.course_number.__hash__()
