from click import echo
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from billiken_blueprint.domain import rating
from billiken_blueprint.repositories import (
    identity_user_repository,
    student_repository,
    instructor_repository,
    course_section_repository,
    course_repository,
    rating_repository,
)

# SQLAlchemy
engine = create_async_engine("sqlite+aiosqlite:///data/data.db", echo=True)
async_sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

# Repositories
identity_user_repository = identity_user_repository.IdentityUserRepository(
    async_sessionmaker
)
student_repository = student_repository.StudentRepository(async_sessionmaker)
instructor_repository = instructor_repository.InstructorRepository(async_sessionmaker)
course_section_repository = course_section_repository.CourseSectionRepository(
    async_sessionmaker
)
course_repository = course_repository.CourseRepository(async_sessionmaker)
rating_repository = rating_repository.RatingRepository(async_sessionmaker)
