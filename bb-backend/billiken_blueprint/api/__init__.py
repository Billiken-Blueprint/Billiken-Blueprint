from billiken_blueprint.api import identity, user_info, courses, instructors, ratings

routers = [
    identity.router,
    user_info.router,
    courses.router,
    instructors.router,
    ratings.router,
]

__all__ = ["routers"]
