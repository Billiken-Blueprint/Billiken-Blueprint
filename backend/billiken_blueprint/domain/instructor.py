from dataclasses import dataclass
from typing import Optional


@dataclass
class Professor:
    id: Optional[int]
    name: str
    rmp_rating: Optional[float] = None
    rmp_num_ratings: Optional[int] = None
    rmp_url: Optional[str] = None
    department: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "rmp_rating": self.rmp_rating,
            "rmp_num_ratings": self.rmp_num_ratings,
            "rmp_url": self.rmp_url,
            "department": self.department,
        }

    @staticmethod
    def from_dict(data: dict) -> "Professor":
        return Professor(
            id=data.get("id"),
            name=data["name"],
            rmp_rating=data.get("rmp_rating"),
            rmp_num_ratings=data.get("rmp_num_ratings"),
            rmp_url=data.get("rmp_url"),
            department=data.get("department"),
        )
