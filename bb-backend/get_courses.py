from billiken_blueprint import courses_at_slu
from billiken_blueprint.domain import course
from billiken_blueprint.domain.course import Course
import asyncio


async def main():
    courses = await courses_at_slu.get_courses(
        keyword="csci", semester=courses_at_slu.Semester.SPRING
    )
    crns_by_code = {}
    for course in courses:
        crns_by_code[course.code] = crns_by_code.get(course.code, [])
        crns_by_code[course.code].append(course.crn)

    for code, crns in crns_by_code.items():
        for crn in crns:
            section = await courses_at_slu.get_section(
                code, crn, crns, semester=courses_at_slu.Semester.SPRING
            )
            print(section)


if __name__ == "__main__":
    looper = asyncio.get_event_loop()
    looper.run_until_complete(main())
