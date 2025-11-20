from ast import Await
import os
import pickle
from billiken_blueprint import services
import billiken_blueprint
from billiken_blueprint.courses_at_slu import get_courses
import billiken_blueprint.courses_at_slu
from billiken_blueprint.courses_at_slu.semester import Semester
from billiken_blueprint.degree_works import (
    get_degree_requirements,
    Majors,
    Colleges,
    Degrees,
    DegreeWorksAuth,
)
from os import environ

from billiken_blueprint.degree_works.api import DegreeWorksDegree, DegreeWorksDegrees
from billiken_blueprint.domain.course import Course, MinimalCourse
from billiken_blueprint.domain.course_attribute import CourseAttribute, CourseAttributes
from billiken_blueprint.domain.section import Section

with open("cookie.txt", "r") as f:
    AUTH_COOKIE = f.read().strip()
BANNER_ID = environ.get("BANNER_ID")


async def get_degree_tracks():
    if not AUTH_COOKIE or not BANNER_ID:
        print("Please create cookie.txt file and set BANNER_ID environment variable.")
        return

    auth_info = DegreeWorksAuth(auth_cookie=AUTH_COOKIE, banner_id=BANNER_ID)
    for degree_name, major in vars(DegreeWorksDegrees).items():
        if not isinstance(major, DegreeWorksDegree):
            continue
        fname = f"{major.major}-{major.degree_type}-{major.college}.json"
        if os.path.exists(f"data/degree_tracks/{fname}"):
            print(f"Data for {degree_name} already exists, skipping...")
            continue
        print(f"Fetching data for {degree_name}...")
        result = await get_degree_requirements(
            major.major, major.degree_type, major.college, auth_info
        )
        services.degree_requirements_repository.save(
            major.major, major.degree_type, major.college, result
        )


async def get_courses_with_attributes():
    attributes = [
        ca for ca in vars(CourseAttributes).values() if isinstance(ca, CourseAttribute)
    ]
    courses: dict[str, billiken_blueprint.courses_at_slu.Course] = {}
    courses_attributes = {}
    for attribute in attributes:
        result = await get_courses(
            keyword=None,
            semester=Semester.SPRING,
            attribute_tag=attribute.courses_slu_label,
        )
        print(attribute.courses_slu_label, [r.code for r in result])
        for r in result:
            courses[r.crn] = r
            courses_attributes.setdefault(r.crn, []).append(attribute)

    for crn in courses.keys():
        print("Section CRN", crn)
        c = courses[crn]
        attributes = courses_attributes.get(crn, [])
        mc = MinimalCourse(None, c.code.split()[0], c.code.split()[1], attributes)
        await services.mccourse_repository.save(mc)

        try:
            section = await billiken_blueprint.courses_at_slu.get_section(
                c.code,
                crn,
                [crn],
                semester=Semester.SPRING,
            )
        except:
            continue
        await services.section_repository.save(
            Section(
                None,
                crn,
                section.instructor_names,
                section.campus_code,
                section.description,
                section.title,
                c.code,
                semester=Semester.SPRING,
            )
        )


async def get_courses_with_codes():
    codes = ["csci", "math"]
    for code in codes:
        result = await get_courses(
            keyword=code, semester=Semester.SPRING, attribute_tag=None
        )
        crns_by_code = {}
        courses_by_code = {}
        for c in result:
            print("Course code:", c.code)

            crns_by_code[c.code] = crns_by_code.get(c.code, [])
            crns_by_code[c.code].append(c.crn)
            courses_by_code[c.code] = c

        for code in crns_by_code.keys():
            c = courses_by_code[code]
            mc = await services.mccourse_repository.get_by_code(*c.code.split())
            if not mc:
                mc = MinimalCourse(None, c.code.split()[0], c.code.split()[1], [])
                await services.mccourse_repository.save(mc)
            for crn in crns_by_code[code]:
                print("Section CRN", crn)
                try:
                    section = await billiken_blueprint.courses_at_slu.get_section(
                        c.code,
                        crn,
                        [crn],
                        semester=Semester.SPRING,
                    )
                except:
                    continue
                await services.section_repository.save(
                    Section(
                        None,
                        crn,
                        section.instructor_names,
                        section.campus_code,
                        section.description,
                        section.title,
                        c.code,
                        semester=Semester.SPRING,
                    )
                )


async def main():
    # await get_degree_tracks()
    # await get_courses_with_attributes()
    await get_courses_with_codes()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
