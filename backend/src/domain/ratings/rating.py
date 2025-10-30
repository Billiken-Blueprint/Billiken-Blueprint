import dataclasses


@dataclasses.dataclass
class Rating:
    id: str
    professor_id: str
    course_id: str | None
    rating: int
