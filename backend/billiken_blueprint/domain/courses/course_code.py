from dataclasses import dataclass


@dataclass
class CourseCode:
    major_code: str
    course_number: str

    def __hash__(self) -> int:
        return hash((self.major_code, self.course_number))

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, CourseCode):
            return False
        return (self.major_code, self.course_number) == (
            value.major_code,
            value.course_number,
        )
