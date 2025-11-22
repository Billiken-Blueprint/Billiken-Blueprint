import json
from urllib import response
from yaml import serialize

from billiken_blueprint import services
from billiken_blueprint.courses_at_slu.course_prereqs_gemini import parse_prereqs
from billiken_blueprint.domain.course_prereq import CoursePrereq
from billiken_blueprint.scheduling import parse_course_reqs

base_path = "data/course_requirements/"

with open("response_cache.json", "r") as f:
    response_cache = json.load(f)

capps = [r for r in response_cache.values() if "capp" in r]
capps_by_code = {}
for capp in capps:
    code = capp["code"]
    capps_by_code.setdefault(code, set()).add(capp["capp"])

capps_by_code = {k: list(v)[0] for k, v in capps_by_code.items()}


async def main():
    for code, capp in capps_by_code.items():
        course_req = services.course_requirements_repository.get_for_code(code)
        if course_req:
            print("Course requirements found for", code, " Continuing")
            continue
        elif capp.strip():
            print(f"No course requirements found for {code}")
            course_req = parse_prereqs(capp)
            prereq = CoursePrereq.from_dict(course_req)
            print("Saving", course_req)
            services.course_requirements_repository.save(code, prereq)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
