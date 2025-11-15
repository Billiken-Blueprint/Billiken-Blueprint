"""
This metadata package exists to be imported by Alembic to simplify database migrations.
"""

from billiken_blueprint.base import Base
from billiken_blueprint.identity.identity_user import IdentityUser
from billiken_blueprint.repositories.student_repository import DBStudent
from billiken_blueprint.repositories.course_repository import DBCourse
from billiken_blueprint.repositories.course_section_repository import DBCourseSection
from billiken_blueprint.repositories.instructor_repository import DBInstructor
from billiken_blueprint.repositories.rating_repository import DBRating

__all__ = [
    "Base",
    "IdentityUser",
    "DBStudent",
    "DBCourse",
    "DBCourseSection",
    "DBInstructor",
    "DBRating",
]
