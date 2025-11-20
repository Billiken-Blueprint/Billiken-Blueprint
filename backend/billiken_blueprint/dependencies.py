from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from yaml import Token

from billiken_blueprint import config, services
from billiken_blueprint.domain.degree import Degree
from billiken_blueprint.identity.token_payload import TokenPayload
from billiken_blueprint.repositories.course_repository import CourseRepository
from billiken_blueprint.repositories.degree_repository import DegreeRepository
from billiken_blueprint.repositories.degree_requirements_repository import (
    DegreeRequirementsRepository,
)
from billiken_blueprint.repositories.identity_user_repository import (
    IdentityUserRepository,
)
from billiken_blueprint.repositories.instructor_repository import InstructorRepository
from billiken_blueprint.repositories.rating_repository import RatingRepository
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


def get_instructor_repository():
    """Get the instructor repository instance.

    This is the single source of truth for the instructor repository dependency.
    Override this in tests to use a test repository.
    """
    return services.instructor_repository


def get_rating_repository():
    """Get the rating repository instance.

    This is the single source of truth for the rating repository dependency.
    Override this in tests to use a test repository.
    """
    return services.rating_repository


def get_degree_repository():
    return services.degree_repository


def get_degree_requirements_repository():
    return services.degree_requirements_repository


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="identity/token")
AuthToken = Annotated[str, Depends(oauth2_scheme)]


def get_auth_payload(token: AuthToken):
    try:
        payload = jwt.decode(token, config.JWT_PUBLIC_KEY, algorithms=["EdDSA"])
        return TokenPayload(sub=payload["sub"], email=payload["email"])
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


AuthPayload = Annotated[TokenPayload, Depends(get_auth_payload)]


# Common type annotations for use in route functions
IdentityUserRepo = Annotated[
    IdentityUserRepository, Depends(get_identity_user_repository)
]
StudentRepo = Annotated[StudentRepository, Depends(get_student_repository)]
CourseRepo = Annotated[CourseRepository, Depends(get_course_repository)]
InstructorRepo = Annotated[InstructorRepository, Depends(get_instructor_repository)]
RatingRepo = Annotated[RatingRepository, Depends(get_rating_repository)]
DegreeRepo = Annotated[DegreeRepository, Depends(get_degree_repository)]
DegreeRequirementsRepo = Annotated[
    DegreeRequirementsRepository, Depends(get_degree_requirements_repository)
]
