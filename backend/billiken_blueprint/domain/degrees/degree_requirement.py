from dataclasses import dataclass
from typing import Generator, Sequence

from billiken_blueprint.domain.courses.course import Course, CourseWithAttributes
from billiken_blueprint.domain.courses.course_code import CourseCode


@dataclass
class CourseWithCode:
    major_code: str
    course_number: str

    def is_satisfied_by(self, course_code: CourseCode) -> bool:
        return (
            self.major_code == course_code.major_code
            and self.course_number == course_code.course_number
        )

    def to_dict(self) -> dict:
        return {
            "$type": "code",
            "major_code": self.major_code,
            "course_number": self.course_number,
        }

    @staticmethod
    def from_dict(data: dict) -> "CourseWithCode":
        return CourseWithCode(
            major_code=data["major_code"],
            course_number=data["course_number"],
        )


@dataclass
class CourseInRange:
    major_code: str
    course_number: str
    end_course_number: str

    def is_satisfied_by(self, course_code: CourseCode) -> bool:
        if course_code.major_code != self.major_code:
            return False
        return (
            int(self.course_number)
            <= int(course_code.course_number)
            <= int(self.end_course_number)
        )

    def to_dict(self) -> dict:
        return {
            "$type": "range",
            "major_code": self.major_code,
            "course_number": self.course_number,
            "end_course_number": self.end_course_number,
        }

    @staticmethod
    def from_dict(data: dict) -> "CourseInRange":
        return CourseInRange(
            major_code=data["major_code"],
            course_number=data["course_number"],
            end_course_number=data["end_course_number"],
        )


@dataclass
class CourseWithAttribute:
    attribute_names: Sequence[str]

    def is_satisfied_by(self, course: CourseWithAttributes) -> bool:
        attribute_labels = [attr.degree_works_label for attr in course.attributes]
        return any(attr in attribute_labels for attr in self.attribute_names)

    def to_dict(self) -> dict:
        return {
            "$type": "attribute",
            "attribute_names": self.attribute_names,
        }

    @staticmethod
    def from_dict(data: dict) -> "CourseWithAttribute":
        return CourseWithAttribute(
            attribute_names=data["attribute_names"],
        )


@dataclass
class CourseRule:
    courses: Sequence[CourseWithCode | CourseInRange | CourseWithAttribute]
    exclude: Sequence[CourseWithCode]

    def to_dict(self) -> dict:
        return {
            "courses": [course.to_dict() for course in self.courses],
            "exclude": [course.to_dict() for course in self.exclude],
        }

    @staticmethod
    def from_dict(data: dict) -> "CourseRule":
        courses = []
        for course_data in data["courses"]:
            if course_data["$type"] == "code":
                courses.append(CourseWithCode.from_dict(course_data))
            elif course_data["$type"] == "range":
                courses.append(CourseInRange.from_dict(course_data))
            elif course_data["$type"] == "attribute":
                courses.append(CourseWithAttribute.from_dict(course_data))

        exclude = [
            CourseWithCode.from_dict(course_data) for course_data in data["exclude"]
        ]

        return CourseRule(courses=courses, exclude=exclude)

    def is_satisfied_by(self, course: CourseWithAttributes) -> bool:
        return not any(
            exclude.is_satisfied_by(course) for exclude in self.exclude
        ) and any(c.is_satisfied_by(course) for c in self.courses)

    def filter_satisfying_courses(
        self, courses: Sequence[CourseWithAttributes]
    ) -> Generator[Course]:
        return (course for course in courses if self.is_satisfied_by(course))


@dataclass
class DegreeRequirement:
    label: str
    needed: int
    course_rules: CourseRule

    def __post_init__(self):
        self.needed = int(self.needed)

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "needed": self.needed,
            "course_rules": self.course_rules.to_dict(),
        }

    @staticmethod
    def from_dict(data: dict) -> "DegreeRequirement":
        return DegreeRequirement(
            label=data["label"],
            needed=data["needed"],
            course_rules=CourseRule.from_dict(data["course_rules"]),
        )

    def is_satisfied_by(self, courses: Sequence[CourseWithAttributes]) -> bool:
        satisfied_count = 0
        for course in courses:
            if self.course_rules.is_satisfied_by(course):
                satisfied_count += 1
            if satisfied_count >= self.needed:
                return True
        return False

    def filter_for_untaken_satisfying_courses(
        self,
        all_courses: Sequence[CourseWithAttributes],
        courses_taken: Sequence[CourseWithAttributes],
    ) -> Sequence[CourseWithAttributes]:
        courses_taken_set = set(courses_taken)
        return [
            course
            for course in all_courses
            if course not in courses_taken_set
            and self.course_rules.is_satisfied_by(course)
        ]
