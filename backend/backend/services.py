from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from repositories.course_repository import CourseRepository
from repositories.identity_user_repository import (
    IdentityUserRepository,
)
from repositories.user_repository import UserRepository

engine = create_async_engine("sqlite+aiosqlite:///data/data.db", echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False)

identity_user_repository = IdentityUserRepository(async_session)
user_repository = UserRepository(async_session)
courses_repository = CourseRepository(async_session)
