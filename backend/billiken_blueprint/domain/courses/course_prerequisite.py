from dataclasses import dataclass
import stat
from typing import Literal, Sequence

from billiken_blueprint.domain.courses.course_code import CourseCode


@dataclass
class CourseCoursePrerequisite:
    major_code: str
    course_number: str
    end_number: int | None
    concurrent_allowed: bool

    def to_dict(self) -> dict:
        return {
            "major_code": self.major_code,
            "course_number": self.course_number,
            "end_number": self.end_number,
            "concurrent_allowed": self.concurrent_allowed,
        }

    @staticmethod
    def from_dict(data: dict) -> "CourseCoursePrerequisite":
        return CourseCoursePrerequisite(
            major_code=data["major_code"],
            course_number=str(data["course_number"]),
            end_number=int(data["end_number"]) if data.get("end_number") else None,
            concurrent_allowed=data["concurrent_allowed"],
        )

    def is_satisfied_by(self, course: CourseCode) -> bool:
        if course.major_code != self.major_code:
            return False
        try:
            course_num = int(course.course_number)
        except ValueError:
            return course.course_number == self.course_number
        if course_num < int(self.course_number):
            return False
        if self.end_number is not None and course_num > self.end_number:
            return False
        return True


@dataclass
class NestedCoursePrerequisite:
    operator: Literal["AND", "OR"]
    operands: "list[CourseCoursePrerequisite | NestedCoursePrerequisite]"

    def is_satisfied_by(self, courses: Sequence[CourseCode]) -> bool:
        if self.operator == "AND":
            return all(
                (
                    any(operand.is_satisfied_by(course) for course in courses)
                    if isinstance(operand, CourseCoursePrerequisite)
                    else operand.is_satisfied_by(courses)
                )
                for operand in self.operands
            )
        elif self.operator == "OR":
            return any(
                (
                    any(operand.is_satisfied_by(course) for course in courses)
                    if isinstance(operand, CourseCoursePrerequisite)
                    else operand.is_satisfied_by(courses)
                )
                for operand in self.operands
            )
        return False

    def filter_for_satisfying_courses(
        self, courses: Sequence[CourseCode]
    ) -> Sequence[CourseCode]:
        return [course for course in courses if self.is_satisfied_by([course])]

    def to_dict(self) -> dict:
        return {
            "operator": self.operator,
            "operands": [
                (
                    operand.to_dict()
                    if isinstance(operand, CourseCoursePrerequisite)
                    else operand.to_dict()
                )
                for operand in self.operands
            ],
        }

    @staticmethod
    def from_dict(data: dict) -> "NestedCoursePrerequisite":
        return NestedCoursePrerequisite(
            operator=data["operator"],
            operands=[
                (
                    NestedCoursePrerequisite.from_dict(operand)
                    if "operator" in operand
                    else CourseCoursePrerequisite.from_dict(operand)
                )
                for operand in data["operands"]
            ],
        )


CoursePrerequisite = NestedCoursePrerequisite
