from dataclasses import asdict, dataclass

from billiken_blueprint.domain.courses.course_attribute import CourseAttribute
from billiken_blueprint.domain.courses.course_code import CourseCode
from billiken_blueprint.domain.courses.course_prerequisite import CoursePrerequisite
from billiken_blueprint.repositories.course_attribute_repository import (
    CourseAttributeRepository,
)


@dataclass
class Course(CourseCode):
    id: int | None
    attribute_ids: list[int]
    prerequisites: CoursePrerequisite | None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "major_code": self.major_code,
            "course_number": self.course_number,
            "attribute_ids": self.attribute_ids,
            "prerequisites": (
                self.prerequisites.to_dict() if self.prerequisites else None
            ),
        }

    @staticmethod
    def from_dict(data: dict) -> "Course":
        return Course(
            id=data.get("id"),
            major_code=data["major_code"],
            course_number=data["course_number"],
            attribute_ids=data["attribute_ids"],
            prerequisites=(
                CoursePrerequisite.from_dict(data["prerequisites"])
                if data.get("prerequisites")
                else None
            ),
        )


@dataclass
class CourseWithAttributes(Course):
    attributes: list[CourseAttribute]

    @staticmethod
    async def from_course(
        course: Course, course_attribute_repository: CourseAttributeRepository
    ):
        attributes = [
            await course_attribute_repository.get_by_id(attr_id)
            for attr_id in course.attribute_ids
        ]
        return CourseWithAttributes(
            major_code=course.major_code,
            course_number=course.course_number,
            id=course.id,
            attribute_ids=course.attribute_ids,
            prerequisites=course.prerequisites,
            attributes=attributes,
        )

    def __hash__(self) -> int:
        return hash((self.major_code, self.course_number))
