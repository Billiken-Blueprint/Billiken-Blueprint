from billiken_blueprint.api import (
    identity,
    user_info,
    courses,
    instructors,
    ratings,
    degrees,
    degree_requirements,
    student_courses,
)

routers = [
    identity.router,
    user_info.router,
    courses.router,
    instructors.router,
    ratings.router,
    degrees.router,
    degree_requirements.router,
    student_courses.router,
]

__all__ = ["routers"]
