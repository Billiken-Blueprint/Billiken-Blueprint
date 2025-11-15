from dataclasses import dataclass


@dataclass
class Course:
    code: str
    title: str
    crn: str
