import pytest
import os
import json
import tempfile
from pathlib import Path
from billiken_blueprint.repositories.degree_repository import DegreeRepository
from billiken_blueprint.domain.degrees.degree import Degree
from billiken_blueprint.domain.degrees.degree_requirement import (
    DegreeRequirement,
    CourseRule,
    CourseWithCode,
)


@pytest.mark.asyncio
class TestDegreeRepository:
    """Test suite for DegreeRepository."""

    def _create_simple_requirement(
        self, label: str, needed: int = 1
    ) -> DegreeRequirement:
        """Helper to create a simple degree requirement."""
        course_rule = CourseRule(
            courses=[
                CourseWithCode(major_code="CSCI", course_number="1000"),
            ],
            exclude=[],
        )
        return DegreeRequirement(
            label=label,
            needed=needed,
            course_rules=course_rule,
        )

    async def test_save_new_degree(self, degree_repository: DegreeRepository):
        """Test saving a new degree to the database."""
        # Create degree requirements
        requirements = [
            self._create_simple_requirement("General Education"),
            self._create_simple_requirement("Core Courses", 2),
        ]

        degree = Degree(
            id=None,
            name="Bachelor of Science in Computer Science",
            degree_works_major_code="CS",
            degree_works_degree_type="BS",
            degree_works_college_code="ENGI",
            requirements=requirements,
        )

        saved = await degree_repository.save(degree)

        assert saved.id is not None
        assert saved.name == "Bachelor of Science in Computer Science"
        assert len(saved.requirements) == 2

    async def test_save_and_update_degree(self, degree_repository: DegreeRepository):
        """Test saving and then updating a degree."""
        # Create and save a new degree
        requirements1 = [
            self._create_simple_requirement("Intro Courses"),
        ]

        degree = Degree(
            id=None,
            name="Bachelor of Science in Mathematics",
            degree_works_major_code="MATH",
            degree_works_degree_type="BS",
            degree_works_college_code="ARTS",
            requirements=requirements1,
        )
        saved = await degree_repository.save(degree)
        degree_id = saved.id

        # Update the degree with different requirements
        requirements2 = [
            self._create_simple_requirement("Intro Courses"),
            self._create_simple_requirement("Advanced Courses", 3),
        ]

        updated_degree = Degree(
            id=degree_id,
            name="Bachelor of Science in Mathematics",
            degree_works_major_code="MATH",
            degree_works_degree_type="BS",
            degree_works_college_code="ARTS",
            requirements=requirements2,
        )
        result = await degree_repository.save(updated_degree)

        assert result.id == degree_id
        assert len(result.requirements) == 2

    async def test_get_by_id(self, degree_repository: DegreeRepository):
        """Test retrieving a degree by ID."""
        # Save a degree first
        requirements = [
            self._create_simple_requirement("Physics Core"),
        ]

        degree = Degree(
            id=None,
            name="Bachelor of Science in Physics",
            degree_works_major_code="PHYS",
            degree_works_degree_type="BS",
            degree_works_college_code="ARTS",
            requirements=requirements,
        )
        saved = await degree_repository.save(degree)
        assert saved.id is not None

        # Retrieve it
        retrieved = await degree_repository.get_by_id(saved.id)

        assert retrieved is not None
        assert retrieved.id == saved.id
        assert retrieved.name == "Bachelor of Science in Physics"
        assert len(retrieved.requirements) == 1

    async def test_get_by_id_not_found(self, degree_repository: DegreeRepository):
        """Test retrieving a non-existent degree raises ValueError."""
        with pytest.raises(ValueError):
            await degree_repository.get_by_id(9999)

    async def test_get_all_empty(self, degree_repository: DegreeRepository):
        """Test getting all degrees when database is empty."""
        degrees = await degree_repository.get_all()
        assert degrees == []

    async def test_get_all_multiple_degrees(self, degree_repository: DegreeRepository):
        """Test retrieving all degrees when multiple exist."""
        # Save multiple degrees
        req1 = [self._create_simple_requirement("Requirements 1")]
        req2 = [self._create_simple_requirement("Requirements 2", 2)]
        req3 = [self._create_simple_requirement("Requirements 3", 3)]

        degree1 = Degree(
            id=None,
            name="Degree 1",
            degree_works_major_code="MAJ1",
            degree_works_degree_type="BS",
            degree_works_college_code="COL1",
            requirements=req1,
        )
        degree2 = Degree(
            id=None,
            name="Degree 2",
            degree_works_major_code="MAJ2",
            degree_works_degree_type="BA",
            degree_works_college_code="COL2",
            requirements=req2,
        )
        degree3 = Degree(
            id=None,
            name="Degree 3",
            degree_works_major_code="MAJ3",
            degree_works_degree_type="BS",
            degree_works_college_code="COL3",
            requirements=req3,
        )

        await degree_repository.save(degree1)
        await degree_repository.save(degree2)
        await degree_repository.save(degree3)

        # Get all degrees
        all_degrees = await degree_repository.get_all()

        assert len(all_degrees) == 3
        assert all(isinstance(d, Degree) for d in all_degrees)
        names = [d.name for d in all_degrees]
        assert "Degree 1" in names
        assert "Degree 2" in names
        assert "Degree 3" in names

    async def test_save_requirements_for_degree(
        self, degree_repository: DegreeRepository
    ):
        """Test saving requirements for a specific degree."""
        # First save a degree
        initial_reqs = [self._create_simple_requirement("Initial")]

        degree = Degree(
            id=None,
            name="Test Degree",
            degree_works_major_code="TEST",
            degree_works_degree_type="BS",
            degree_works_college_code="TEST",
            requirements=initial_reqs,
        )
        saved = await degree_repository.save(degree)
        assert saved.id is not None
        degree_id = saved.id

        # Update requirements
        new_reqs = [
            self._create_simple_requirement("Updated"),
            self._create_simple_requirement("New", 2),
        ]

        await degree_repository.save_requirements_for_degree(degree_id, new_reqs)

        # Retrieve the degree and verify requirements are updated
        retrieved = await degree_repository.get_by_id(degree_id)
        assert len(retrieved.requirements) == 2

    async def test_get_requirements_for_degree_not_found(
        self, degree_repository: DegreeRepository
    ):
        """Test getting requirements for non-existent degree raises ValueError."""
        with pytest.raises(ValueError):
            await degree_repository.get_requirements_for_degree(9999)
