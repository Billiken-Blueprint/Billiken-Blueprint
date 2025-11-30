"""
This metadata package exists to be imported by Alembic to simplify database migrations.
"""

from billiken_blueprint.base import Base
from billiken_blueprint.identity.identity_user import DBIdentityUser
from billiken_blueprint.repositories.student_repository import DBStudent
from billiken_blueprint.repositories.course_repository import DBCourse
from billiken_blueprint.repositories.instructor_repository import DBInstructor
from billiken_blueprint.repositories.rating_repository import DBRating
from billiken_blueprint.repositories.section_repository import DBSection
from billiken_blueprint.repositories.rmp_review_repository import DBRmpReview
from billiken_blueprint.repositories.degree_repository import DBDegree
from billiken_blueprint.repositories.course_attribute_repository import (
    DBCourseAttribute,
)

__all__ = [
    "Base",
    "DBIdentityUser",
    "DBStudent",
    "DBCourse",
    "DBInstructor",
    "DBRating",
    "DBSection",
    "DBRmpReview",
    "DBDegree",
    "DBCourseAttribute",
]
