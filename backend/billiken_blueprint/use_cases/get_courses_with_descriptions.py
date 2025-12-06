from collections import defaultdict
from billiken_blueprint.domain.courses.course import Course, CourseWithDescription
from billiken_blueprint.domain.section import Section
from typing import Sequence

def get_courses_with_descriptions(
    courses: Sequence[Course], 
    sections: Sequence[Section]
) -> Sequence[CourseWithDescription]:
    course_by_code = {f"{course.major_code} {course.course_number}": course for course in courses}
    descriptions_by_course_code = defaultdict(set[str])
    for section in sections:
        descriptions_by_course_code[section.course_code].add(section.description)

    return [CourseWithDescription(
        major_code=course_by_code[course_code].major_code, 
        course_number=course_by_code[course_code].course_number,
        id=course_by_code[course_code].id,
        attribute_ids=course_by_code[course_code].attribute_ids,
        prerequisites=course_by_code[course_code].prerequisites,
        description=descriptions.pop()
    ) 
        for course_code, descriptions in descriptions_by_course_code.items() 
        if len(descriptions) == 1]
