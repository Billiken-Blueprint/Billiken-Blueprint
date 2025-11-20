from dataclasses import dataclass
import operator


@dataclass
class CoursePrereqNode:
    course_code: str
    to: int | None = None
    concurrent: bool = False


@dataclass
class Operand:
    operator: str
    operands: list[Operand | CoursePrereqNode]


@dataclass
class CoursePrerequisite:
    course_code: str
    reqs: Operand | CoursePrereqNode | None
