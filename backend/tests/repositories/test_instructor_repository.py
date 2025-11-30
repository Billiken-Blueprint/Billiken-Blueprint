import pytest
from billiken_blueprint.repositories.instructor_repository import InstructorRepository
from billiken_blueprint.domain.instructor import Professor


@pytest.mark.asyncio
class TestInstructorRepository:
    """Test suite for InstructorRepository."""

    async def test_save_new_instructor(
        self, instructor_repository: InstructorRepository
    ):
        """Test saving a new instructor to the database."""
        professor = Professor(
            id=None,
            name="Dr. John Smith",
            rmp_rating=4.5,
            rmp_num_ratings=120,
            rmp_url="https://www.ratemyprofessors.com/professor/123456",
            department="Computer Science",
        )

        saved = await instructor_repository.save(professor)

        assert saved.id is not None
        assert saved.name == "Dr. John Smith"

    async def test_save_and_update_instructor(
        self, instructor_repository: InstructorRepository
    ):
        """Test saving and then updating an instructor."""
        # Create and save a new instructor
        professor = Professor(
            id=None,
            name="Dr. Jane Doe",
            rmp_rating=3.8,
            rmp_num_ratings=50,
            rmp_url="https://www.ratemyprofessors.com/professor/654321",
            department="Mathematics",
        )
        saved = await instructor_repository.save(professor)
        instructor_id = saved.id

        # Update the instructor - need to create a new professor with the same id
        # and save it to simulate an update
        updated_professor = Professor(
            id=instructor_id,
            name="Dr. Jane Doe",
            rmp_rating=4.2,
            rmp_num_ratings=65,
            rmp_url="https://www.ratemyprofessors.com/professor/654321",
            department="Mathematics",
        )
        result = await instructor_repository.save(updated_professor)

        assert result.id == instructor_id

    async def test_get_by_id(self, instructor_repository: InstructorRepository):
        """Test retrieving an instructor by ID."""
        # Save an instructor first
        professor = Professor(
            id=None,
            name="Dr. Alice Johnson",
            rmp_rating=4.7,
            rmp_num_ratings=200,
            rmp_url="https://www.ratemyprofessors.com/professor/111111",
            department="Physics",
        )
        saved = await instructor_repository.save(professor)
        assert saved.id is not None

        # Retrieve it
        retrieved = await instructor_repository.get_by_id(saved.id)

        assert retrieved is not None
        assert retrieved.id == saved.id
        assert retrieved.name == "Dr. Alice Johnson"
        assert retrieved.rmp_rating == 4.7

    async def test_get_by_id_not_found(
        self, instructor_repository: InstructorRepository
    ):
        """Test retrieving a non-existent instructor returns None."""
        result = await instructor_repository.get_by_id(9999)
        assert result is None

    async def test_get_by_name(self, instructor_repository: InstructorRepository):
        """Test retrieving an instructor by name."""
        # Save an instructor
        professor = Professor(
            id=None,
            name="Dr. Bob Williams",
            rmp_rating=3.5,
            rmp_num_ratings=75,
            rmp_url="https://www.ratemyprofessors.com/professor/222222",
            department="Chemistry",
        )
        saved = await instructor_repository.save(professor)

        # Retrieve by name
        retrieved = await instructor_repository.get_by_name("Dr. Bob Williams")

        assert retrieved is not None
        assert retrieved.id == saved.id
        assert retrieved.name == "Dr. Bob Williams"

    async def test_get_by_name_not_found(
        self, instructor_repository: InstructorRepository
    ):
        """Test retrieving a non-existent instructor by name returns None."""
        result = await instructor_repository.get_by_name("Dr. Nonexistent")
        assert result is None

    async def test_get_all_empty(self, instructor_repository: InstructorRepository):
        """Test getting all instructors when database is empty."""
        instructors = await instructor_repository.get_all()
        assert instructors == []

    async def test_get_all_multiple_instructors(
        self, instructor_repository: InstructorRepository
    ):
        """Test retrieving all instructors when multiple exist."""
        # Save multiple instructors
        prof1 = Professor(
            id=None,
            name="Dr. Professor One",
            rmp_rating=4.0,
            rmp_num_ratings=50,
            rmp_url="https://www.ratemyprofessors.com/professor/1",
            department="CS",
        )
        prof2 = Professor(
            id=None,
            name="Dr. Professor Two",
            rmp_rating=3.5,
            rmp_num_ratings=40,
            rmp_url="https://www.ratemyprofessors.com/professor/2",
            department="MATH",
        )
        prof3 = Professor(
            id=None,
            name="Dr. Professor Three",
            rmp_rating=4.5,
            rmp_num_ratings=100,
            rmp_url="https://www.ratemyprofessors.com/professor/3",
            department="PHYS",
        )

        await instructor_repository.save(prof1)
        await instructor_repository.save(prof2)
        await instructor_repository.save(prof3)

        # Get all instructors
        all_instructors = await instructor_repository.get_all()

        assert len(all_instructors) == 3
        assert all(isinstance(p, Professor) for p in all_instructors)
        names = [p.name for p in all_instructors]
        assert "Dr. Professor One" in names
        assert "Dr. Professor Two" in names
        assert "Dr. Professor Three" in names

    async def test_save_instructor_minimal_fields(
        self, instructor_repository: InstructorRepository
    ):
        """Test saving an instructor with only required fields."""
        professor = Professor(
            id=None,
            name="Dr. Minimal Info",
        )

        saved = await instructor_repository.save(professor)

        assert saved.id is not None
        assert saved.name == "Dr. Minimal Info"
        assert saved.rmp_rating is None
        assert saved.rmp_num_ratings is None
