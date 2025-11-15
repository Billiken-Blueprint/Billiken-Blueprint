from dataclasses import dataclass

from billiken_blueprint.domain.course import Course


@dataclass
class GradRequirement:
    id: int
    credits_needed: int
    satisfied_by_course_ids: list[int]
