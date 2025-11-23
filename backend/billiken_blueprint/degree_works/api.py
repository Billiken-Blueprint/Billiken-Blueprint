from dataclasses import dataclass
import json
from operator import ne
from typing import TYPE_CHECKING

import httpx

from billiken_blueprint.degree_works.course import (
    DegreeWorksAnyCourseWithAttribute,
    DegreeWorksCourseGroup,
    DegreeWorksCourseRange,
    DegreeWorksCourse,
)

if TYPE_CHECKING:
    from billiken_blueprint.domain.degree import DegreeRequirement


class Majors:
    CSCI = "CS"
    MATH = "MATH"


class Degrees:
    BA = "BA"
    BS = "BS"


class Colleges:
    SSE = "SSE"
    AS = "AS"


@dataclass
class DegreeWorksAuth:
    auth_cookie: str
    banner_id: str


@dataclass
class DegreeWorksDegree:
    major: str
    degree_type: str
    college: str


class DegreeWorksDegrees:
    math_ba = DegreeWorksDegree(
        major=Majors.MATH,
        degree_type=Degrees.BA,
        college=Colleges.AS,
    )
    math_bs = DegreeWorksDegree(
        major=Majors.MATH,
        degree_type=Degrees.BS,
        college=Colleges.SSE,
    )
    cs_ba = DegreeWorksDegree(
        major=Majors.CSCI,
        degree_type=Degrees.BA,
        college=Colleges.SSE,
    )
    cs_bs = DegreeWorksDegree(
        major=Majors.CSCI,
        degree_type=Degrees.BS,
        college=Colleges.SSE,
    )


def req_to_degree_requirement(req: dict, label: str) -> "DegreeRequirement":
    from billiken_blueprint.domain.degree import DegreeRequirement

    needed = req.get("classesBegin", 1)
    course_array = req["courseArray"]
    courses = []
    for course in course_array:
        if course["discipline"] == "@" and course["number"] == "@":
            courses.append(
                DegreeWorksAnyCourseWithAttribute(
                    attributes=course["withArray"][0]["valueList"]
                )
            )
        elif "numberEnd" in course:
            courses.append(
                DegreeWorksCourseRange(
                    major_code=course["discipline"],
                    course_number=course["number"],
                    end_course_number=course["numberEnd"],
                )
            )
        else:
            courses.append(
                DegreeWorksCourse(
                    major_code=course["discipline"],
                    course_number=course["number"],
                )
            )

    exclude = []
    if "except" in req:
        for course in req["except"]["courseArray"]:
            exclude.append(
                DegreeWorksCourse(
                    major_code=course["discipline"],
                    course_number=course["number"],
                )
            )

    return DegreeRequirement(
        label=label,
        needed=needed,
        course_group=DegreeWorksCourseGroup(courses=courses, exclude=exclude),
    )


def parse_rule_array(rule_array: list[dict]) -> list["DegreeRequirement"]:
    reqs = []
    for rule in rule_array:
        if "ruleArray" in rule:
            reqs.extend(parse_rule_array(rule["ruleArray"]))
        elif "requirement" in rule and "courseArray" in rule["requirement"]:
            label = rule["label"]
            req = rule["requirement"]
            reqs.append(req_to_degree_requirement(req, label))

    return reqs


async def get_degree_requirements(
    major: str,
    degree_type: str,
    college: str,
    auth_info: DegreeWorksAuth,
    catalog_year: str = "2025",
) -> list["DegreeRequirement"]:

    url = "https://degree-works.slu.edu:8546/ResponsiveDashboard/api/audit"

    payload = json.dumps(
        {
            "studentId": "001272417",
            "isIncludeInprogress": True,
            "isIncludePreregistered": True,
            "isKeepCurriculum": False,
            "school": "UG",
            "degree": degree_type,
            "catalogYear": catalog_year,
            "goals": [
                {"code": "MAJOR", "value": major, "catalogYear": ""},
                # {"code": "PROGRAM", "value": program, "catalogYear": ""},
                {"code": "COLLEGE", "value": college, "catalogYear": ""},
            ],
            "classes": [],
        }
    )

    # headers = {
    #    "Content-Type": "application/json",
    #    "Pragma": "no-cache",
    #    "Accept": "*/*",
    #    "Sec-Fetch-Site": "same-origin",
    #    "Accept-Language": "en-US,en;q=0.9",
    #    "Cache-Control": "no-cache",
    #    "Sec-Fetch-Mode": "cors",
    #    "Accept-Encoding": "gzip, deflate, br",
    #    "Origin": "https://degree-works.slu.edu:8546",
    #    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.1 Safari/605.1.15",
    #    "Referer": "https://degree-works.slu.edu:8546/ResponsiveDashboard/worksheets/whatif",
    #    "Connection": "keep-alive",
    #    "Sec-Fetch-Dest": "empty",
    #    "Priority": "u=3, i",
    # }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, content=payload)
        response.raise_for_status()
        response = response.json()

    cores = parse_rule_array(
        next(
            block
            for block in response["blockArray"]
            if block["requirementValue"] == "COREUNIV"
        )["ruleArray"]
    )

    majors = parse_rule_array(
        next(
            block
            for block in response["blockArray"]
            if block["requirementType"] == "MAJOR"
        )["ruleArray"]
    )

    return cores + majors
