from curses import start_color
from dataclasses import dataclass


@dataclass
class MeetingTime:
    day: int
    start_time: str
    end_time: str


@dataclass
class Section:
    meeting_times: list[MeetingTime]
    instructor_names: list[str]
    campus_code: str
    description: str
    title: str
