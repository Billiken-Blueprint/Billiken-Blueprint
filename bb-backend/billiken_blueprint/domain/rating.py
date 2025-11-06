from dataclasses import dataclass


@dataclass
class Rating:
    id: int
    course_id: int
    professor_id: int
    student_id: int
    rating_value: float
