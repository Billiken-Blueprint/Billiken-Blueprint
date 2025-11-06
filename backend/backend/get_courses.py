import asyncio
from courses import get_courses_from_slu, Semester
import services


async def main():
    courses = get_courses_from_slu(Semester.SPRING, "csci")
    for course in courses:
        await services.courses_repository.save(course)


if __name__ == "__main__":
    looper = asyncio.get_event_loop()
    looper.run_until_complete(main())
