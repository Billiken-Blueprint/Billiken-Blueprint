import pytest
import pytest_asyncio

from billiken_blueprint.domain.student import Student
from billiken_blueprint.repositories.student_repository import (
    StudentRepository,
    DBStudent,
)


@pytest_asyncio.fixture
async def repository(async_sessionmaker):
    """Create a StudentRepository instance."""
    return StudentRepository(async_sessionmaker)


@pytest.mark.asyncio
class TestStudentRepository:
    async def test_save_new_student(self, repository, async_sessionmaker):
        """Test saving a new student to the database."""
        # Arrange
        student = Student(
            id=1,
            name="Alice Johnson",
            degree_ids=[1, 2],
            major_code="CSCI",
            degree_type="BS",
            college="College of Arts and Sciences",
            graduation_year=2025,
            completed_course_ids=[101, 102, 103],
        )

        # Act
        await repository.save(student)

        # Assert - verify it was saved
        async with async_sessionmaker() as session:
            result = await session.get(DBStudent, 1)
            assert result is not None
            assert result.name == "Alice Johnson"
            assert result.degree_ids == [1, 2]
            assert result.completed_course_ids == [101, 102, 103]

    async def test_save_updates_existing_student(self, repository, async_sessionmaker):
        """Test that saving a student with existing ID updates it."""
        # Arrange - save initial student
        student1 = Student(
            id=1,
            name="Bob Smith",
            degree_ids=[1],
            major_code="MATH",
            degree_type="BS",
            college="College of Arts and Sciences",
            graduation_year=2024,
            completed_course_ids=[101],
        )
        await repository.save(student1)

        # Act - update the student
        student2 = Student(
            id=1,
            name="Bob Smith Jr.",
            degree_ids=[1, 2],
            major_code="MATH",
            degree_type="BA",
            college="College of Arts and Sciences",
            graduation_year=2024,
            completed_course_ids=[101, 102],
        )
        await repository.save(student2)

        # Assert - verify it was updated, not duplicated
        async with async_sessionmaker() as session:
            result = await session.get(DBStudent, 1)
            assert result is not None
            assert result.name == "Bob Smith Jr."
            assert result.degree_ids == [1, 2]
            assert result.completed_course_ids == [101, 102]

    async def test_save_student_with_empty_lists(self, repository, async_sessionmaker):
        """Test saving a student with empty degree and course lists."""
        # Arrange
        student = Student(
            id=1,
            name="Charlie Davis",
            degree_ids=[],
            major_code="ENGR",
            degree_type="BS",
            college="Parks College of Engineering",
            graduation_year=2026,
            completed_course_ids=[],
        )

        # Act
        await repository.save(student)

        # Assert
        async with async_sessionmaker() as session:
            result = await session.get(DBStudent, 1)
            assert result is not None
            assert result.name == "Charlie Davis"
            assert result.degree_ids == []
            assert result.completed_course_ids == []

    async def test_save_student_with_none_id(self, repository, async_sessionmaker):
        """Test saving a student with None as ID (should auto-generate)."""
        # Arrange
        student = Student(
            id=None,
            name="Diana Evans",
            degree_ids=[3],
            major_code="BIOL",
            degree_type="BS",
            college="College of Arts and Sciences",
            graduation_year=2027,
            completed_course_ids=[],
        )

        # Act
        await repository.save(student)

        # Assert - verify it was saved with an auto-generated ID
        async with async_sessionmaker() as session:
            # Since we don't know the auto-generated ID, we'll query by name
            # This assumes you have a get_by_name method or similar
            # For now, we'll just check that at least one student exists
            from sqlalchemy import select

            stmt = select(DBStudent).where(DBStudent.name == "Diana Evans")
            result = await session.execute(stmt)
            db_student = result.scalar_one_or_none()

            assert db_student is not None
            assert db_student.id is not None  # Auto-generated
            assert db_student.name == "Diana Evans"
            assert db_student.degree_ids == [3]

    async def test_save_multiple_students(self, repository, async_sessionmaker):
        """Test saving multiple students."""
        # Arrange
        students = [
            Student(
                id=1,
                name="Student One",
                degree_ids=[1],
                major_code="PHYS",
                degree_type="BS",
                college="College of Arts and Sciences",
                graduation_year=2025,
                completed_course_ids=[101],
            ),
            Student(
                id=2,
                name="Student Two",
                degree_ids=[2],
                major_code="CHEM",
                degree_type="BS",
                college="College of Arts and Sciences",
                graduation_year=2026,
                completed_course_ids=[102],
            ),
            Student(
                id=3,
                name="Student Three",
                degree_ids=[1, 2],
                major_code="CSCI",
                degree_type="BS",
                college="College of Arts and Sciences",
                graduation_year=2024,
                completed_course_ids=[101, 102],
            ),
        ]

        # Act
        for student in students:
            await repository.save(student)

        # Assert - verify all were saved
        async with async_sessionmaker() as session:
            result1 = await session.get(DBStudent, 1)
            result2 = await session.get(DBStudent, 2)
            result3 = await session.get(DBStudent, 3)

            assert result1.name == "Student One"
            assert result2.name == "Student Two"
            assert result3.name == "Student Three"

    async def test_save_student_with_many_courses(self, repository, async_sessionmaker):
        """Test saving a student with many completed courses."""
        # Arrange
        student = Student(
            id=1,
            name="Overachiever",
            degree_ids=[1],
            major_code="LIBT",
            degree_type="BA",
            college="College of Arts and Sciences",
            graduation_year=2023,
            completed_course_ids=list(range(100, 200)),  # 100 courses
        )

        # Act
        await repository.save(student)

        # Assert
        async with async_sessionmaker() as session:
            result = await session.get(DBStudent, 1)
            assert result is not None
            assert len(result.completed_course_ids) == 100
            assert result.completed_course_ids[0] == 100
            assert result.completed_course_ids[-1] == 199
