from dataclasses import dataclass
from pydoc import describe


@dataclass
class MeetingTime:
    day: int
    start_time: str
    end_time: str


@dataclass
class Section:
    id: int | None
    crn: str
    instructor_names: list[str]
    campus_code: str
    description: str
    title: str
    course_code: str
    semester: str
    meeting_times: list[MeetingTime]
