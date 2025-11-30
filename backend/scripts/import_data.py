import os
import sys
from dump_data import base_path
import json
from pathlib import Path

# Add the parent directory to the path so we can import billiken_blueprint
sys.path.insert(0, str(Path(__file__).parent.parent))

from billiken_blueprint import services
from billiken_blueprint.domain.courses.course import Course
from billiken_blueprint.domain.degrees.degree import Degree
from billiken_blueprint.domain.section import Section
from billiken_blueprint.domain.instructor import Professor
from billiken_blueprint.domain.courses.course_attribute import CourseAttribute


async def main():
    # Import courses
    with open(os.path.join(base_path, "courses.json"), "r") as f:
        courses_data = json.load(f)
    for course_dict in courses_data:
        await services.course_repository.save(Course.from_dict(course_dict))

    # Import instructors
    with open(os.path.join(base_path, "instructors.json"), "r") as f:
        instructors_data = json.load(f)
    for instructor_dict in instructors_data:
        await services.instructor_repository.save(Professor.from_dict(instructor_dict))

    # Import sections
    with open(os.path.join(base_path, "sections.json"), "r") as f:
        sections_data = json.load(f)
    for section_dict in sections_data:
        await services.section_repository.save(Section.from_dict(section_dict))

    # Import degrees
    with open(os.path.join(base_path, "degrees.json"), "r") as f:
        degrees_data = json.load(f)
    for degree_dict in degrees_data:
        await services.degree_repository.save(Degree.from_dict(degree_dict))

    # Import course attributes
    with open(os.path.join(base_path, "attributes.json"), "r") as f:
        attributes_data = json.load(f)
    for attribute_dict in attributes_data:
        await services.course_attribute_repository.save(
            CourseAttribute.from_dict(attribute_dict)
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
