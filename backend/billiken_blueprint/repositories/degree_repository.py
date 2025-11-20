import yaml
import os

from billiken_blueprint.degree_works.api import DegreeWorksDegree, DegreeWorksDegrees
from billiken_blueprint.domain.degree import DegreeRequirement

BASE_PATH = "data/degree_tracks"


class DegreeRepository:
    def get_all(self):
        splits = [name[0:-5].split("-") for name in os.listdir(BASE_PATH)]
        return [DegreeWorksDegree(s[0], s[1], s[2]) for s in splits]
