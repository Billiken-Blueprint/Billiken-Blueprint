import dataclasses


@dataclasses.dataclass
class User:
    id: str
    majors: list[str]
    minors: list[str]
