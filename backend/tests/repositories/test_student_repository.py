import pytest
from billiken_blueprint.repositories.student_repository import StudentRepository
from billiken_blueprint.domain.student import Student


@pytest.mark.asyncio
class TestStudentRepository:
    """Test suite for StudentRepository."""

    async def test_save_new_student(self, student_repository: StudentRepository):
        """Test saving a new student to the database."""
        student = Student(
            id=None,
            name="John Doe",
            degree_id=1,
            graduation_year=2025,
            completed_course_ids=[101, 102, 103],
            unavailability_times=[],
            avoid_times=[],
        )

        saved = await student_repository.save(student)

        assert saved.id is not None
        assert saved.name == "John Doe"
        assert saved.graduation_year == 2025

    async def test_save_and_update_student(self, student_repository: StudentRepository):
        """Test saving and then updating a student."""
        # Create and save a new student
        student = Student(
            id=None,
            name="Jane Smith",
            degree_id=1,
            graduation_year=2026,
            completed_course_ids=[201, 202],
            unavailability_times=[],
            avoid_times=[],
        )
        saved = await student_repository.save(student)
        student_id = saved.id

        # Update the student
        updated_student = Student(
            id=student_id,
            name="Jane Smith",
            degree_id=2,
            graduation_year=2026,
            completed_course_ids=[201, 202, 203, 204],
            unavailability_times=[],
            avoid_times=[],
        )
        result = await student_repository.save(updated_student)

        assert result.id == student_id
        assert len(result.completed_course_ids) == 4

    async def test_get_by_id(self, student_repository: StudentRepository):
        """Test retrieving a student by ID."""
        # Save a student first
        student = Student(
            id=None,
            name="Bob Johnson",
            degree_id=3,
            graduation_year=2024,
            completed_course_ids=[301, 302],
            unavailability_times=[],
            avoid_times=[],
        )
        saved = await student_repository.save(student)
        assert saved.id is not None

        # Retrieve it
        retrieved = await student_repository.get_by_id(saved.id)

        assert retrieved is not None
        assert retrieved.id == saved.id
        assert retrieved.name == "Bob Johnson"
        assert retrieved.degree_id == 3
        assert retrieved.graduation_year == 2024

    async def test_get_by_id_not_found(self, student_repository: StudentRepository):
        """Test retrieving a non-existent student returns None."""
        result = await student_repository.get_by_id(9999)
        assert result is None

    async def test_save_student_with_empty_lists(
        self, student_repository: StudentRepository
    ):
        """Test saving a student with empty degree and course lists."""
        student = Student(
            id=None,
            name="Alice Williams",
            degree_id=1,
            graduation_year=2027,
            completed_course_ids=[],
            unavailability_times=[],
            avoid_times=[],
        )

        saved = await student_repository.save(student)

        assert saved.id is not None
        assert saved.completed_course_ids == []

    async def test_save_student_with_many_courses(
        self, student_repository: StudentRepository
    ):
        """Test saving a student with many completed courses."""
        many_courses = list(range(1000, 1050))  # 50 courses
        student = Student(
            id=None,
            name="Charlie Brown",
            degree_id=1,
            graduation_year=2023,
            completed_course_ids=many_courses,
            unavailability_times=[],
            avoid_times=[],
        )

        saved = await student_repository.save(student)

        assert saved.id is not None
        assert len(saved.completed_course_ids) == 50
        assert saved.completed_course_ids == many_courses

    async def test_save_student_with_time_slots(
        self, student_repository: StudentRepository
    ):
        """Test saving a student with unavailability and avoid times."""
        from billiken_blueprint.domain.student import TimeSlot

        unavailability = [TimeSlot(day=1, start="1000", end="1200")]
        avoid = [TimeSlot(day=5, start="1400", end="1600")]

        student = Student(
            id=None,
            name="Time Keeper",
            degree_id=1,
            graduation_year=2025,
            completed_course_ids=[101],
            unavailability_times=unavailability,
            avoid_times=avoid,
        )

        saved = await student_repository.save(student)
        assert saved.id is not None

        # Verify we can retrieve the student with time slots
        retrieved = await student_repository.get_by_id(saved.id)
        assert retrieved is not None
        assert len(retrieved.unavailability_times) == 1
        assert retrieved.unavailability_times[0].day == 1
        assert retrieved.unavailability_times[0].start == "1000"
        assert retrieved.unavailability_times[0].end == "1200"
        assert len(retrieved.avoid_times) == 1
        assert retrieved.avoid_times[0].day == 5
        assert retrieved.avoid_times[0].start == "1400"
        assert retrieved.avoid_times[0].end == "1600"

    async def test_save_student_with_empty_time_slots(
        self, student_repository: StudentRepository
    ):
        """Test saving a student with empty time slot lists."""
        from billiken_blueprint.domain.student import TimeSlot

        student = Student(
            id=None,
            name="No Times",
            degree_id=1,
            graduation_year=2025,
            completed_course_ids=[102],
            unavailability_times=[],
            avoid_times=[],
        )

        saved = await student_repository.save(student)
        assert saved.id is not None

        retrieved = await student_repository.get_by_id(saved.id)
        assert retrieved is not None
        assert retrieved.unavailability_times == []
        assert retrieved.avoid_times == []

