from billiken_blueprint.api import (
    identity,
    user_info,
    courses,
    instructors,
    ratings,
    degrees,
    degree_requirements,
)

from billiken_blueprint.scheduling import schedule_router

routers = [
    identity.router,
    user_info.router,
    courses.router,
    instructors.router,
    ratings.router,
    degrees.router,
    degree_requirements.router,
    schedule_router.router,
]

__all__ = ["routers"]
