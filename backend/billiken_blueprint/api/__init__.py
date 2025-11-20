from billiken_blueprint.api import (
    identity,
    user_info,
    courses,
    instructors,
    ratings,
    degrees,
    degree_requirements,
)

routers = [
    identity.router,
    user_info.router,
    courses.router,
    instructors.router,
    ratings.router,
    degrees.router,
    degree_requirements.router,
]

__all__ = ["routers"]
