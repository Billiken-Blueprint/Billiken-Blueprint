from importlib.abc import MetaPathFinder
from dataclasses import dataclass, field
from typing import Sequence

from billiken_blueprint.domain.courses.course import CourseCode, CourseWithAttributes
from billiken_blueprint.domain.degrees.degree_requirement import (
    DegreeRequirement,
)
from billiken_blueprint.domain.section import Section, MeetingTime
from billiken_blueprint.domain.student import TimeSlot


def check_time_overlap(time_slot: TimeSlot, meeting_time: MeetingTime) -> bool:
    return meeting_time.overlaps(
        MeetingTime(
            day=time_slot.day,
            start_time=time_slot.start,
            end_time=time_slot.end,
        )
    )


def section_overlaps_timeslots(section: Section, time_slots: Sequence[TimeSlot]) -> bool:
    if section.course_code == 'CSCI 2300':
        print(time_slots)
        print(section.meeting_times)
        print(section.instructor_names)
    for time_slot in time_slots:
        for meeting_time in section.meeting_times:
            if check_time_overlap(time_slot, meeting_time):
                return True
    return False


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

    MAJOR_CODE_MAPPING = {
        "CS": "CSCI",
        # Add other mappings as needed
    }

    @property
    def course_major_code(self) -> str:
        return self.MAJOR_CODE_MAPPING.get(
            self.degree_works_major_code, self.degree_works_major_code
        )

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

    