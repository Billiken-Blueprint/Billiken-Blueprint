from dataclasses import dataclass
from typing import Optional


@dataclass
class Professor:
    id: Optional[int]
    name: str
