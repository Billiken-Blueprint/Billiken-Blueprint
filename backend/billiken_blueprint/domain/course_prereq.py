from dataclasses import dataclass
import stat
from typing import Literal, Sequence

from billiken_blueprint.domain.course import MinimalCourse


@dataclass
class CoursePrereqCourse:
    major_code: str
    course_number: int
    end_number: int | None
    concurrent_allowed: bool

    def to_dict(self) -> dict:
        return {
            "major_code": self.major_code,
            "course_number": self.course_number,
            "end_number": self.end_number,
            "concurrent_allowed": self.concurrent_allowed,
        }


@dataclass
class NestedRequirement:
    operator: Literal["AND", "OR"]
    operands: "Sequence[CoursePrereqCourse | NestedRequirement]"

    def is_satisfied_by(self, courses: Sequence[MinimalCourse]) -> bool:
        if self.operator == "AND":
            return all(
                (
                    any(
                        course.major_code == operand.major_code
                        and operand.course_number <= int(course.course_number)
                        and (
                            operand.end_number is None
                            or int(course.course_number) <= operand.end_number
                        )
                        for course in courses
                    )
                    if isinstance(operand, CoursePrereqCourse)
                    else operand.is_satisfied_by(courses)
                )
                for operand in self.operands
            )
        elif self.operator == "OR":
            return any(
                (
                    any(
                        course.major_code == operand.major_code
                        and operand.course_number <= int(course.course_number)
                        and (
                            operand.end_number is None
                            or int(course.course_number) <= operand.end_number
                        )
                        for course in courses
                    )
                    if isinstance(operand, CoursePrereqCourse)
                    else operand.is_satisfied_by(courses)
                )
                for operand in self.operands
            )
        else:
            raise ValueError(f"Unknown operator: {self.operator}")

    @staticmethod
    def from_dict(data: dict) -> "NestedRequirement":
        return NestedRequirement(
            operator=data["operator"],
            operands=[
                (
                    CoursePrereqCourse(
                        major_code=operand["major_code"],
                        course_number=operand["course_number"],
                        end_number=operand.get("end_number", operand["course_number"]),
                        concurrent_allowed=operand.get("concurrent_allowed", False),
                    )
                    if "major_code" in operand
                    else NestedRequirement.from_dict(operand)
                )
                for operand in data["operands"]
            ],
        )

    def to_dict(self) -> dict:
        return {
            "operator": self.operator,
            "operands": [
                (
                    operand.to_dict()
                    if isinstance(operand, NestedRequirement)
                    else operand.to_dict()
                )
                for operand in self.operands
            ],
        }


CoursePrereq = NestedRequirement
