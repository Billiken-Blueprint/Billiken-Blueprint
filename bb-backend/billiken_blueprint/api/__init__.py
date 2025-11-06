from billiken_blueprint.api import identity, user_info

routers = [identity.router, user_info.router]

__all__ = ["routers"]
