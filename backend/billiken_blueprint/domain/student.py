from dataclasses import dataclass
from typing import Optional


@dataclass
class TimeSlot:
    day: int
    start: str  # HHMM format
    end: str    # HHMM format

    def to_dict(self) -> dict:
        """Convert TimeSlot to dict for JSON storage."""
        return {"day": self.day, "start": self.start, "end": self.end}

    @classmethod
    def from_dict(cls, data: dict) -> "TimeSlot":
        """Create TimeSlot from dict loaded from JSON storage."""
        return cls(day=data["day"], start=data["start"], end=data["end"])


@dataclass
class Student:
    id: Optional[int]
    name: str
    degree_id: int
    graduation_year: int
    completed_course_ids: list[int]
    unavailability_times: list[TimeSlot]
    avoid_times: list[TimeSlot]
