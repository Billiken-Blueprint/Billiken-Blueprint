from dataclasses import dataclass, field
from typing import Sequence

from billiken_blueprint.domain.courses.course import CourseCode, CourseWithAttributes
from billiken_blueprint.domain.degrees.degree_requirement import (
    DegreeRequirement,
)
from billiken_blueprint.domain.section import Section


@dataclass
class SectionWithRequirementsFulfilled:
    section: Section
    fulfilled_requirements: Sequence[str] = field(default_factory=list)


@dataclass
class DegreeWorksDegree:
    degree_works_major_code: str
    degree_works_degree_type: str
    degree_works_college_code: str


@dataclass
class Degree(DegreeWorksDegree):
    id: int | None
    name: str
    requirements: Sequence[DegreeRequirement]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "degree_works_major_code": self.degree_works_major_code,
            "degree_works_degree_type": self.degree_works_degree_type,
            "degree_works_college_code": self.degree_works_college_code,
            "requirements": [req.to_dict() for req in self.requirements],
        }

    @staticmethod
    def from_dict(data: dict) -> "Degree":
        return Degree(
            id=data.get("id"),
            name=data["name"],
            degree_works_major_code=data["degree_works_major_code"],
            degree_works_degree_type=data["degree_works_degree_type"],
            degree_works_college_code=data["degree_works_college_code"],
            requirements=[
                DegreeRequirement.from_dict(req) for req in data["requirements"]
            ],
        )

    def get_recommended_sections(
        self,
        taken_courses: Sequence[CourseWithAttributes],
        all_courses: Sequence[CourseWithAttributes],
        all_sections: Sequence[Section],
        course_equivalencies: Sequence[Sequence[CourseCode]],
    ) -> Sequence[SectionWithRequirementsFulfilled]:
        # Same scoring mechanism as last implementation,
        # but this time we should first check which courses
        # satisfy degree requirements. Then we should traverse the
        # dependency tree to get all courses a part of the tree.
        # And we should add 1 to the score of that course.
        # This way, courses that are a part of more dependency
        # trees are prioritized first.
        # Then, we rank sections by the score of their courses.
        # Then, we can take N sections that haven't been taken yet
        # and have their course's requirements satisfied.

        # Parse equivalencies into a lookup map.
        equivalency_map = {}
        for i, equivalency_group in enumerate(course_equivalencies):
            for course_code in equivalency_group:
                equivalency_map[course_code] = i

        # Get unfulfilled requirements.
        fulfilled_reqs = [
            c for c in self.requirements if c.is_satisfied_by(taken_courses)
        ]
        unfulfilled_reqs = [c for c in self.requirements if c not in fulfilled_reqs]

        # Score courses based on how many courses they are prerequisites for.
        course_scores = {}
        course_eq_scores = {}
        for req in unfulfilled_reqs:
            courses = req.filter_for_untaken_satisfying_courses(
                all_courses, taken_courses
            )
            for course in courses:
                if course.prerequisites is None:
                    continue
                for prereq in course.prerequisites.filter_for_satisfying_courses(
                    all_courses
                ):
                    course_scores[prereq] = course_scores.get(prereq, 0) + 1
                    if prereq in equivalency_map:
                        course_eq_scores[equivalency_map[prereq]] = (
                            course_eq_scores.get(equivalency_map[prereq], 0) + 1
                        )
                course_scores[course] = course_scores.get(course, 0) + 1
                if course in equivalency_map:
                    course_eq_scores[equivalency_map[course]] = (
                        course_eq_scores.get(equivalency_map[course], 0) + 1
                    )

        for code, group_num in equivalency_map.items():
            if group_num in course_eq_scores:
                course_scores[code] = course_eq_scores[group_num]

        # Score sections based on their course scores.
        course_codes_to_course = {
            f"{c.major_code} {c.course_number}": c for c in course_scores.keys()
        }
        sections = [
            section
            for section in all_sections
            if section.course_code in course_codes_to_course
        ]
        sections_sorted = sorted(
            sections,
            key=lambda s: course_scores[course_codes_to_course[s.course_code]],
            reverse=True,
        )

        return [
            SectionWithRequirementsFulfilled(section=section)
            for section in sections_sorted
        ]
