import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker as asm,
    AsyncSession,
)

from billiken_blueprint.base import Base
from billiken_blueprint.dependencies import (
    get_identity_user_repository,
    get_student_repository,
    get_mc_course_repository,
)
from billiken_blueprint.repositories.identity_user_repository import (
    IdentityUserRepository,
)
from billiken_blueprint.repositories.student_repository import StudentRepository
from billiken_blueprint.repositories.mc_course_repository import MCCourseRepository
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
def mc_course_repository(async_sessionmaker):
    """Create a test mc_course repository using in-memory database."""
    return MCCourseRepository(async_sessionmaker)


@pytest.fixture(scope="function")
def app_client(identity_user_repository, student_repository, mc_course_repository):
    """Create a FastAPI test client with overridden dependencies."""
    # Override the dependencies to use test repositories
    app.dependency_overrides[get_identity_user_repository] = (
        lambda: identity_user_repository
    )
    app.dependency_overrides[get_student_repository] = lambda: student_repository
    app.dependency_overrides[get_mc_course_repository] = lambda: mc_course_repository

    test_client = TestClient(app)
    yield test_client

    # Clean up overrides after test
    app.dependency_overrides.clear()
