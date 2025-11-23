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
