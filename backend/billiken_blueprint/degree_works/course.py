from dataclasses import dataclass
from typing import Generator, Sequence

from billiken_blueprint.domain.courses.course import Course


@dataclass
class DegreeWorksCourse:
    major_code: str
    course_number: str

    def is_satisfied_by(self, course: Course) -> bool:
        return (
            course.major_code == self.major_code
            and course.course_number == self.course_number
        )

    def to_dict(self) -> dict:
        return {
            "type": "course",
            "major_code": self.major_code,
            "course_number": self.course_number,
        }

    @staticmethod
    def from_dict(data: dict) -> "DegreeWorksCourse":
        return DegreeWorksCourse(
            major_code=data["major_code"],
            course_number=data["course_number"],
        )


@dataclass
class DegreeWorksCourseRange:
    major_code: str
    course_number: str
    end_course_number: str

    def is_satisfied_by(self, course: Course) -> bool:
        if course.major_code != self.major_code:
            return False
        return (
            int(self.course_number)
            <= int(course.course_number)
            <= int(self.end_course_number)
        )

    def to_dict(self) -> dict:
        return {
            "type": "course_range",
            "major_code": self.major_code,
            "course_number": self.course_number,
            "end_course_number": self.end_course_number,
        }

    @staticmethod
    def from_dict(data: dict) -> "DegreeWorksCourseRange":
        return DegreeWorksCourseRange(
            major_code=data["major_code"],
            course_number=data["course_number"],
            end_course_number=data["end_course_number"],
        )


@dataclass
class DegreeWorksAnyCourseWithAttribute:
    attributes: Sequence[str]

    def to_dict(self) -> dict:
        return {
            "type": "any_with_attribute",
            "attributes": self.attributes,
        }

    @staticmethod
    def from_dict(data: dict) -> "DegreeWorksAnyCourseWithAttribute":
        return DegreeWorksAnyCourseWithAttribute(attributes=data["attributes"])

    def is_satisfied_by(self, course: MinimalCourse) -> bool:
        return any(
            attr.degree_works_label in self.attributes for attr in course.attributes
        )


@dataclass
class DegreeWorksCourseGroup:
    courses: Sequence[
        DegreeWorksCourse | DegreeWorksCourseRange | DegreeWorksAnyCourseWithAttribute
    ]
    exclude: Sequence[DegreeWorksCourse]

    @staticmethod
    def from_dict(data: dict) -> "DegreeWorksCourseGroup":
        courses = []
        for course in data["courses"]:
            if course["type"] == "any_with_attribute":
                courses.append(DegreeWorksAnyCourseWithAttribute.from_dict(course))
            elif course["type"] == "course_range":
                courses.append(DegreeWorksCourseRange.from_dict(course))
            elif course["type"] == "course":
                courses.append(DegreeWorksCourse.from_dict(course))
        exclude = [
            DegreeWorksCourse.from_dict(course) for course in data.get("exclude", [])
        ]
        return DegreeWorksCourseGroup(courses=courses, exclude=exclude)

    def to_dict(self) -> dict:
        return {
            "courses": [course.to_dict() for course in self.courses],
            "exclude": [course.to_dict() for course in self.exclude],
        }

    def is_satisfied_by(self, course: Course) -> bool:
        return not any(excl.is_satisfied_by(course) for excl in self.exclude) and any(
            c.is_satisfied_by(course) for c in self.courses
        )

    def filter_satisfying_courses(self, courses: Sequence[Course]) -> Generator[Course]:
        return (course for course in courses if self.is_satisfied_by(course))
