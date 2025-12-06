from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt

from billiken_blueprint import config, services
from billiken_blueprint.domain.courses.course_attribute import CourseAttribute
from billiken_blueprint.domain.student import Student
from billiken_blueprint.identity.identity_user import IdentityUser
from billiken_blueprint.identity.token_payload import TokenPayload
from billiken_blueprint.repositories.course_attribute_repository import (
    CourseAttributeRepository,
)
from billiken_blueprint.repositories.course_repository import CourseRepository
from billiken_blueprint.repositories.degree_repository import DegreeRepository
from billiken_blueprint.repositories.identity_user_repository import (
    IdentityUserRepository,
)
from billiken_blueprint.repositories.instructor_repository import InstructorRepository
from billiken_blueprint.repositories.rating_repository import RatingRepository
from billiken_blueprint.repositories.rmp_review_repository import RmpReviewRepository
from billiken_blueprint.repositories.student_repository import StudentRepository
from billiken_blueprint.repositories.section_repository import SectionRepository
import chromadb


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


def get_rmp_review_repository():
    """Get the RMP review repository instance.

    This is the single source of truth for the RMP review repository dependency.
    Override this in tests to use a test repository.
    """
    return services.rmp_review_repository


def get_degree_repository():
    return services.degree_repository


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="identity/token", auto_error=False)
AuthToken = Annotated[Optional[str], Depends(oauth2_scheme)]


def get_auth_payload(token: AuthToken):
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
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


def get_course_attribute_repository():
    return services.course_attribute_repository


CourseAttributeRepo = Annotated[
    CourseAttributeRepository, Depends(get_course_attribute_repository)
]


def get_optional_auth_payload(token: Optional[str] = Depends(oauth2_scheme)):
    """Get auth payload if token is provided, otherwise return None."""
    if token is None:
        return None
    try:
        payload = jwt.decode(token, config.JWT_PUBLIC_KEY, algorithms=["EdDSA"])
        return TokenPayload(sub=payload["sub"], email=payload["email"])
    except (
        jwt.InvalidTokenError,
        jwt.DecodeError,
        jwt.ExpiredSignatureError,
        Exception,
    ):
        # Return None for any token-related errors to allow unauthenticated access
        return None


OptionalAuthPayload = Annotated[
    Optional[TokenPayload], Depends(get_optional_auth_payload)
]


def get_section_repository() -> SectionRepository:
    """Get the section repository instance.

    This is the single source of truth for the section repository dependency.
    Override this in tests to use a test repository.
    """
    return services.section_repository

def get_course_descriptions_collection() -> chromadb.Collection:
    """Get the course descriptions collection instance."""
    from billiken_blueprint.chromadb import course_descriptions_collection
    
    return course_descriptions_collection

# Common type annotations for use in route functions
IdentityUserRepo = Annotated[
    IdentityUserRepository, Depends(get_identity_user_repository)
]
StudentRepo = Annotated[StudentRepository, Depends(get_student_repository)]
CourseRepo = Annotated[CourseRepository, Depends(get_course_repository)]
InstructorRepo = Annotated[InstructorRepository, Depends(get_instructor_repository)]
RatingRepo = Annotated[RatingRepository, Depends(get_rating_repository)]
RmpReviewRepo = Annotated[RmpReviewRepository, Depends(get_rmp_review_repository)]
DegreeRepo = Annotated[DegreeRepository, Depends(get_degree_repository)]
SectionRepo = Annotated[SectionRepository, Depends(get_section_repository)]
CourseDescriptionsCollection = Annotated[chromadb.Collection, Depends(get_course_descriptions_collection)]


async def get_current_identity(auth: AuthPayload, repo: IdentityUserRepo):
    user = await repo.get_by_id(int(auth.sub))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


CurrentIdentity = Annotated[IdentityUser, Depends(get_current_identity)]


async def get_current_student(identity: CurrentIdentity, repo: StudentRepo):
    if identity.student_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    student = await repo.get_by_id(identity.student_id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    return student


CurrentStudent = Annotated[Student, Depends(get_current_student)]
