from dataclasses import dataclass
from typing import Sequence

from billiken_blueprint.degree_works.course import DegreeWorksCourseGroup
from billiken_blueprint.domain.course import MinimalCourse


@dataclass
class DegreeRequirement:
    label: str
    needed: int
    course_group: DegreeWorksCourseGroup

    def is_satisfied_by(self, courses: Sequence[MinimalCourse]) -> bool:
        satisfied_count = 0
        for course in courses:
            if self.course_group.is_satisfied_by(course):
                satisfied_count += 1
                if satisfied_count >= self.needed:
                    return True
        return False

    def filter_untaken_courses_satisfying_requirement(
        self, courses: Sequence[MinimalCourse], courses_taken: Sequence[MinimalCourse]
    ) -> list[MinimalCourse]:
        courses_taken_set = set(courses_taken)
        courses = [course for course in courses if course not in courses_taken_set]
        satisfying_courses = []
        for course in courses:
            if self.course_group.is_satisfied_by(course):
                satisfying_courses.append(course)
        return satisfying_courses


@dataclass
class Degree:
    name: str
    requirements: list[DegreeRequirement]

    def filter_courses_satisfying_unsatisfied_requirements(
        self,
        courses: Sequence[MinimalCourse],
        courses_taken: Sequence[MinimalCourse],
    ) -> Sequence[MinimalCourse]:
        reqs = [
            req for req in self.requirements if not req.is_satisfied_by(courses_taken)
        ]
        satisfying_courses = set(
            course
            for req in reqs
            for course in req.filter_untaken_courses_satisfying_requirement(
                courses, courses_taken
            )
        )
        return list(satisfying_courses)
