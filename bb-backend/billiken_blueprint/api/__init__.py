from billiken_blueprint.api import identity, user_info, courses

routers = [identity.router, user_info.router, courses.router]

__all__ = ["routers"]
