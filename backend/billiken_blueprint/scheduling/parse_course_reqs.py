import yaml
from billiken_blueprint.domain import course
from billiken_blueprint.scheduling.course_prereq import (
    CoursePrerequisite,
    Operand,
    CoursePrereqNode,
)


def parse_req(yaml_obj: dict):
    if "operator" in yaml_obj:
        return Operand(
            operator=yaml_obj["operator"],
            operands=[parse_req(op) for op in yaml_obj["operands"]],
        )
    else:
        return CoursePrereqNode(
            course_code=yaml_obj["code"],
            to=yaml_obj.get("to"),
            concurrent=yaml_obj.get("concurrent", False),
        )


def parse_reqs(yaml_text: str):
    yml = yaml.safe_load(yaml_text)
    return [
        CoursePrerequisite(
            course_code=course["code"],
            reqs=parse_req(course["reqs"]) if "reqs" in course else None,
        )
        for course in yml["courses"]
    ]
