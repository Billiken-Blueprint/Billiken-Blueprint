import os
import json

from billiken_blueprint.domain.course_prereq import CoursePrereq

base_path = "data/course_requirements"


class CourseRequirementsRepository:
    def get_for_code(self, code: str):
        path = os.path.join(base_path, f"{code}.json")
        if not os.path.exists(path):
            return None
        with open(path, "r") as f:
            data = json.load(f)
        return CoursePrereq.from_dict(data)

    def save(self, code: str, course_prereq: CoursePrereq):
        path = os.path.join(base_path, f"{code}.json")
        with open(path, "w") as f:
            json.dump(course_prereq.to_dict(), f, indent=2)
