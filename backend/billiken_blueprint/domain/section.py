from dataclasses import dataclass
from pydoc import describe


@dataclass
class Section:
    id: int | None
    crn: str
    instructor_names: list[str]
    campus_code: str
    description: str
    title: str
    course_code: str
    semester: str
