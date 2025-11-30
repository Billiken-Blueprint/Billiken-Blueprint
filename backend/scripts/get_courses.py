from sqlalchemy import desc
from websockets import serve
from billiken_blueprint import courses_at_slu, services
from billiken_blueprint.domain import course
from billiken_blueprint.domain.course import Course
import asyncio

from billiken_blueprint.domain.instructor import Professor


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
            instructor_names = section.instructor_names
            db_instructors = []
            course = await services.course_repository.get_by_code(code)
            if not course:
                course = Course(
                    id=None,
                    course_code=code,
                    major=code.split(" ")[0],
                    title=section.title,
                    description=section.description,
                    course_number=code.split(" ")[1],
                )
                course = await services.course_repository.save(course)
            for name in instructor_names:
                db_instructor = await services.instructor_repository.get_by_name(name)
                if not db_instructor:
                    db_instructor = await services.instructor_repository.save(
                        Professor(id=None, name=name)
                    )
                db_instructors.append(db_instructor)
            await services.course_section_repository.save(
                course_section=section,
                course_id=course.id,  # type: ignore
                crn=crn,
                instructor_ids=[
                    instr.id for instr in db_instructors if instr.id is not None
                ],
            )


if __name__ == "__main__":
    asyncio.run(main())
