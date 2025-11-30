from dataclasses import dataclass


@dataclass
class CourseAttribute:
    id: int | None
    name: str
    degree_works_label: str
    courses_at_slu_label: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "degree_works_label": self.degree_works_label,
            "courses_at_slu_label": self.courses_at_slu_label,
        }

    @staticmethod
    def from_dict(data: dict) -> "CourseAttribute":
        return CourseAttribute(
            id=data.get("id"),
            name=data["name"],
            degree_works_label=data["degree_works_label"],
            courses_at_slu_label=data["courses_at_slu_label"],
        )
