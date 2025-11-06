from typing import Annotated

from fastapi import Depends

from billiken_blueprint import services
from billiken_blueprint.repositories.course_repository import CourseRepository
from billiken_blueprint.repositories.identity_user_repository import (
    IdentityUserRepository,
)
from billiken_blueprint.repositories.student_repository import StudentRepository


def get_identity_user_repository() -> IdentityUserRepository:
    """Get the identity user repository instance.

    This is the single source of truth for the identity user repository dependency.
    Override this in tests to use a test repository.
    """
    return services.identity_user_repository


def get_student_repository() -> StudentRepository:
    """Get the student repository instance.

    This is the single source of truth for the student repository dependency.
    Override this in tests to use a test repository.
    """
    return services.student_repository


def get_course_repository() -> CourseRepository:
    """Get the course repository instance.

    This is the single source of truth for the course repository dependency.
    Override this in tests to use a test repository.
    """
    return services.course_repository


# Common type annotations for use in route functions
IdentityUserRepo = Annotated[
    IdentityUserRepository, Depends(get_identity_user_repository)
]
StudentRepo = Annotated[StudentRepository, Depends(get_student_repository)]
CourseRepo = Annotated[CourseRepository, Depends(get_course_repository)]
