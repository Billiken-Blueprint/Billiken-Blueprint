from dataclasses import dataclass
from pydoc import describe


@dataclass
class MeetingTime:
    day: int
    start_time: str
    end_time: str

    def overlaps(self, other: "MeetingTime") -> bool:
        if self.day != other.day:
            return False
        
        start1 = int(self.start_time)
        end1 = int(self.end_time)
        start2 = int(other.start_time)
        end2 = int(other.end_time)

        return max(start1, start2) < min(end1, end2)


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

    def overlaps(self, other: "Section") -> bool:
        return any(
            mt1.overlaps(mt2) for mt1 in self.meeting_times for mt2 in other.meeting_times
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "crn": self.crn,
            "instructor_names": self.instructor_names,
            "campus_code": self.campus_code,
            "description": self.description,
            "title": self.title,
            "course_code": self.course_code,
            "semester": self.semester,
            "meeting_times": [
                {
                    "day": mt.day,
                    "start_time": mt.start_time,
                    "end_time": mt.end_time,
                }
                for mt in self.meeting_times
            ],
        }

    @staticmethod
    def from_dict(data: dict) -> "Section":
        return Section(
            id=data.get("id"),
            crn=data["crn"],
            instructor_names=data["instructor_names"],
            campus_code=data["campus_code"],
            description=data["description"],
            title=data["title"],
            course_code=data["course_code"],
            semester=data["semester"],
            meeting_times=[
                MeetingTime(
                    day=mt["day"],
                    start_time=mt["start_time"],
                    end_time=mt["end_time"],
                )
                for mt in data["meeting_times"]
            ],
        )
