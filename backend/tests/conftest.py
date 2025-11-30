import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker as asm,
    AsyncSession,
)

from billiken_blueprint.base import Base
from billiken_blueprint.repositories.identity_user_repository import (
    IdentityUserRepository,
)
from billiken_blueprint.repositories.student_repository import StudentRepository
from billiken_blueprint.repositories.course_repository import CourseRepository
from billiken_blueprint.repositories.instructor_repository import InstructorRepository
from billiken_blueprint.repositories.degree_repository import DegreeRepository
from billiken_blueprint.repositories.section_repository import SectionRepository
from billiken_blueprint.repositories.rating_repository import RatingRepository
from billiken_blueprint.repositories.course_attribute_repository import (
    CourseAttributeRepository,
)
from billiken_blueprint.repositories.rmp_review_repository import RmpReviewRepository
from server import app


@pytest_asyncio.fixture(scope="session")
async def async_engine():
    """Create an async engine for the test session."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    # Create all tables once for the session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_sessionmaker(async_engine):
    """Create a session maker factory for each test function."""
    sessionmaker = asm(bind=async_engine, expire_on_commit=False, class_=AsyncSession)
    yield sessionmaker

    # Clean up data between tests (but keep schema)
    async with async_engine.begin() as conn:
        # Delete all data from tables but keep the schema
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
        await conn.commit()


@pytest.fixture(scope="function")
def identity_user_repository(async_sessionmaker):
    """Create a test identity user repository using in-memory database."""
    return IdentityUserRepository(async_sessionmaker)


@pytest.fixture(scope="function")
def student_repository(async_sessionmaker):
    """Create a test student repository using in-memory database."""
    return StudentRepository(async_sessionmaker)


@pytest.fixture(scope="function")
def course_repository(async_sessionmaker):
    """Create a test course repository using in-memory database."""
    return CourseRepository(async_sessionmaker)


@pytest.fixture(scope="function")
def instructor_repository(async_sessionmaker):
    """Create a test instructor repository using in-memory database."""
    return InstructorRepository(async_sessionmaker)


@pytest.fixture(scope="function")
def degree_repository(async_sessionmaker):
    """Create a test degree repository using in-memory database."""
    return DegreeRepository(async_sessionmaker)


@pytest.fixture(scope="function")
def section_repository(async_sessionmaker):
    """Create a test section repository using in-memory database."""
    return SectionRepository(async_sessionmaker)


@pytest.fixture(scope="function")
def rating_repository(async_sessionmaker):
    """Create a test rating repository using in-memory database."""
    return RatingRepository(async_sessionmaker)


@pytest.fixture(scope="function")
def course_attribute_repository(async_sessionmaker):
    """Create a test course attribute repository using in-memory database."""
    return CourseAttributeRepository(async_sessionmaker)


@pytest.fixture(scope="function")
def rmp_review_repository(async_sessionmaker):
    """Create a test RMP review repository using in-memory database."""
    return RmpReviewRepository(async_sessionmaker)


@pytest.fixture(scope="function")
def app_client(identity_user_repository, student_repository):
    """Create a FastAPI test client with overridden dependencies."""
    # This fixture is optional and can be extended to override specific dependencies
    test_client = TestClient(app)
    yield test_client

    # Clean up overrides after test
    app.dependency_overrides.clear()
