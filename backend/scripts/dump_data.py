import json
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import billiken_blueprint
sys.path.insert(0, str(Path(__file__).parent.parent))

from billiken_blueprint import services


base_path = "data_dumps/"


async def main():
    # Dump courses
    courses = await services.course_repository.get_all()
    body = [course.to_dict() for course in courses]
    with open(os.path.join(base_path, "courses.json"), "w+") as f:
        json.dump(body, f, indent=2)

    # Dump instructors
    instructors = await services.instructor_repository.get_all()
    body = [instructor.to_dict() for instructor in instructors]
    with open(os.path.join(base_path, "instructors.json"), "w+") as f:
        json.dump(body, f, indent=2)

    # Dump sections
    sections = await services.section_repository.get_all()
    body = [section.to_dict() for section in sections]
    with open(os.path.join(base_path, "sections.json"), "w+") as f:
        json.dump(body, f, indent=2)

    # Dump degrees
    degrees = await services.degree_repository.get_all()
    body = [degree.to_dict() for degree in degrees]
    with open(os.path.join(base_path, "degrees.json"), "w+") as f:
        json.dump(body, f, indent=2)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
