import json
import os
from billiken_blueprint.degree_works.api import req_to_degree_requirement
from billiken_blueprint.degree_works.course import DegreeWorksCourseGroup
from billiken_blueprint.domain.degree import DegreeRequirement
import pickle


BASE_PATH = "data/degree_tracks"


class DegreeRequirementsRepository:
    def get(
        self, major: str, degree_type: str, college: str
    ) -> list[DegreeRequirement] | None:
        path = os.path.join(BASE_PATH, f"{major}-{degree_type}-{college}.json")
        with open(path, "r") as f:
            data = json.load(f)
        return [
            DegreeRequirement(
                req["label"],
                req["needed"],
                DegreeWorksCourseGroup.from_dict(req["course_group"]),
            )
            for req in data
        ]

    def save(
        self,
        major: str,
        degree_type: str,
        college: str,
        degree_requirements: list[DegreeRequirement],
    ) -> None:
        path = os.path.join(BASE_PATH, f"{major}-{degree_type}-{college}.json")
        with open(path, "w") as f:
            json.dump(
                [
                    {
                        "label": dr.label,
                        "needed": dr.needed,
                        "course_group": dr.course_group.to_dict(),
                    }
                    for dr in degree_requirements
                ],
                f,
                indent=2,
            )
