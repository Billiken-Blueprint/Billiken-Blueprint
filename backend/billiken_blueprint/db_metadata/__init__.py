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
<<<<<<< HEAD
from billiken_blueprint.repositories.mc_course_repository import MCCourseDbEntity
from billiken_blueprint.repositories.section_repository import SectionRepositoryDBEntity
=======
from billiken_blueprint.repositories.rmp_review_repository import DBRmpReview
>>>>>>> e4dc8a5461e0eb5e37a8ad25cb236697c9a43fea

__all__ = [
    "Base",
    "IdentityUser",
    "DBStudent",
    "DBCourse",
    "DBCourseSection",
    "DBInstructor",
    "DBRating",
<<<<<<< HEAD
    "MCCourseDbEntity",
    "SectionRepositoryDBEntity",
=======
    "DBRmpReview",
>>>>>>> e4dc8a5461e0eb5e37a8ad25cb236697c9a43fea
]
