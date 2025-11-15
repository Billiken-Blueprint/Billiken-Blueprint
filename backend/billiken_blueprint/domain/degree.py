from dataclasses import dataclass

from billiken_blueprint.domain.grad_requirement import GradRequirement


@dataclass
class Degree:
    id: int
    name: str
    grad_requirement_ids: list[int]
    credits_needed: int
