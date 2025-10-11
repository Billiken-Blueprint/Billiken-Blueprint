import dataclasses


@dataclasses.dataclass
class Offering:
    id: str
    course_id: str
    instructors: list[str]
