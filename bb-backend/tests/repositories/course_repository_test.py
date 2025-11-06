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
class TestCourseRepository:
    async def test_save_new_course(self, repository, async_sessionmaker):
        """Test saving a new course to the database."""
        # Arrange
        course = Course(
            id=1,
            major="CSCI",
            course_number="1050",
            course_code="CSCI-1050",
            credits=3,
        )

        # Act
        await repository.save(course)

        # Assert - verify it was saved
        async with async_sessionmaker() as session:
            result = await session.get(DBCourse, 1)
            assert result is not None
            assert result.code == "CSCI-1050"

    async def test_save_updates_existing_course(self, repository, async_sessionmaker):
        """Test that saving a course with existing ID updates it."""
        # Arrange - save initial course
        course1 = Course(
            id=1,
            major="CSCI",
            course_number="1050",
            course_code="CSCI-1050",
            credits=3,
        )
        await repository.save(course1)

        # Act - update the course
        course2 = Course(
            id=1,
            major="CSCI",
            course_number="1050",
            course_code="CSCI-1050-UPDATED",
            credits=4,
        )
        await repository.save(course2)

        # Assert - verify it was updated, not duplicated
        async with async_sessionmaker() as session:
            result = await session.get(DBCourse, 1)
            assert result is not None
            assert result.code == "CSCI-1050-UPDATED"

    async def test_get_by_id_existing_course(self, repository):
        """Test retrieving an existing course by ID."""
        # Arrange
        course = Course(
            id=42,
            major="MATH",
            course_number="2100",
            course_code="MATH-2100",
            credits=3,
        )
        await repository.save(course)

        # Act
        result = await repository.get_by_id(42)

        # Assert
        assert result is not None
        assert result.id == 42
        assert result.course_code == "MATH-2100"
        assert result.major == "MATH"

    async def test_get_by_id_nonexistent_course(self, repository):
        """Test retrieving a course that doesn't exist returns None."""
        # Act
        result = await repository.get_by_id(999)

        # Assert
        assert result is None

    async def test_get_by_code_existing_course(self, repository):
        """Test retrieving a course by course code."""
        # Arrange
        course = Course(
            id=1,
            major="PHYS",
            course_number="2010",
            course_code="PHYS-2010",
            credits=4,
        )
        await repository.save(course)

        # Act
        result = await repository.get_by_code("PHYS-2010")

        # Assert
        assert result is not None
        assert result.id == 1
        assert result.course_code == "PHYS-2010"

    async def test_get_by_code_nonexistent_course(self, repository):
        """Test retrieving a course by code that doesn't exist returns None."""
        # Act
        result = await repository.get_by_code("FAKE-9999")

        # Assert
        assert result is None

    async def test_get_all_courses(self, repository):
        """Test retrieving all courses from the database."""
        # Arrange - save multiple courses
        courses = [
            Course(1, "CSCI", "1050", "CSCI-1050", 3),
            Course(2, "MATH", "2100", "MATH-2100", 4),
            Course(3, "PHYS", "2010", "PHYS-2010", 4),
        ]
        for course in courses:
            await repository.save(course)

        # Act
        result = await repository.get_all()

        # Assert
        assert len(result) == 3
        assert all(isinstance(c, Course) for c in result)
        course_codes = {c.course_code for c in result}
        assert course_codes == {"CSCI-1050", "MATH-2100", "PHYS-2010"}

    async def test_get_all_empty_database(self, repository):
        """Test getting all courses when database is empty."""
        # Act
        result = await repository.get_all()

        # Assert
        assert result == []

    async def test_delete_existing_course(self, repository):
        """Test deleting a course by ID."""
        # Arrange
        course = Course(1, "CSCI", "1050", "CSCI-1050", 3)
        await repository.save(course)

        # Act
        await repository.delete(1)

        # Assert
        result = await repository.get_by_id(1)
        assert result is None

    async def test_delete_nonexistent_course(self, repository):
        """Test deleting a course that doesn't exist doesn't raise an error."""
        # Act & Assert - should not raise
        await repository.delete(999)

    async def test_search_by_major(self, repository):
        """Test searching courses by major."""
        # Arrange
        courses = [
            Course(1, "CSCI", "1050", "CSCI-1050", 3),
            Course(2, "CSCI", "2100", "CSCI-2100", 3),
            Course(3, "MATH", "2100", "MATH-2100", 4),
        ]
        for course in courses:
            await repository.save(course)

        # Act
        result = await repository.search_by_major("CSCI")

        # Assert
        assert len(result) == 2
        assert all(c.major == "CSCI" for c in result)
