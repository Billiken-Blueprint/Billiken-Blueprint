import pytest
import pytest_asyncio

from billiken_blueprint.domain.course import Course
from billiken_blueprint.repositories.course_repository import (
    CourseRepository,
    DBCourse,
)


@pytest_asyncio.fixture
async def repository(async_sessionmaker):
    """Create a CourseRepository instance."""
    return CourseRepository(async_sessionmaker)


@pytest.mark.asyncio
async def test_save_course(repository, async_sessionmaker):
    """Test saving a course to the database."""
    # Arrange
    course = Course(
        id=1,
        major="CSCI",
        title="Introduction to Computer Science",
        course_number="1050",
        course_code="CSCI 1050",
        description="An intro course to CS",
    )

    # Act
    saved_course = await repository.save(course)

    # Assert
    assert saved_course.id == 1
    assert saved_course.code == "CSCI 1050"


@pytest.mark.asyncio
async def test_get_by_id(repository):
    """Test retrieving a course by ID."""
    # Arrange
    course = Course(
        id=42,
        major="MATH",
        title="Calculus II",
        course_number="2100",
        course_code="MATH 2100",
        description="Advanced calculus",
    )
    await repository.save(course)

    # Act
    result = await repository.get_by_id(42)

    # Assert
    assert result is not None
    assert result.id == 42


@pytest.mark.asyncio
async def test_get_by_id_nonexistent(repository):
    """Test retrieving a nonexistent course returns None."""
    # Act
    result = await repository.get_by_id(999)

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_delete(repository):
    """Test deleting a course by ID."""
    # Arrange
    course = Course(
        id=1,
        major="CSCI",
        title="Intro to CS",
        course_number="1050",
        course_code="CSCI 1050",
        description="Basic CS concepts",
    )
    await repository.save(course)

    # Act
    await repository.delete(1)

    # Assert
    result = await repository.get_by_id(1)
    assert result is None
