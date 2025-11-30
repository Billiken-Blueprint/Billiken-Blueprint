from click import echo
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from billiken_blueprint.repositories import (
    course_attribute_repository,
    degree_repository,
    identity_user_repository,
    section_repository,
    student_repository,
    instructor_repository,
    course_repository,
    rating_repository,
    rmp_review_repository,
)

# SQLAlchemy
engine = create_async_engine("sqlite+aiosqlite:///data/data.db", echo=False)
async_sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

# Repositories
identity_user_repository = identity_user_repository.IdentityUserRepository(
    async_sessionmaker
)
student_repository = student_repository.StudentRepository(async_sessionmaker)
instructor_repository = instructor_repository.InstructorRepository(async_sessionmaker)
course_repository = course_repository.CourseRepository(async_sessionmaker)
rating_repository = rating_repository.RatingRepository(async_sessionmaker)
degree_repository = degree_repository.DegreeRepository(async_sessionmaker)
section_repository = section_repository.SectionRepository(async_sessionmaker)

rmp_review_repository = rmp_review_repository.RmpReviewRepository(async_sessionmaker)
course_attribute_repository = course_attribute_repository.CourseAttributeRepository(
    async_sessionmaker
)
