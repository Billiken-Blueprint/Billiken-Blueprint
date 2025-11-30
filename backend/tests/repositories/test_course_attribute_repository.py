import pytest
from billiken_blueprint.repositories.course_attribute_repository import (
    CourseAttributeRepository,
)
from billiken_blueprint.domain.courses.course_attribute import CourseAttribute


@pytest.mark.asyncio
class TestCourseAttributeRepository:
    """Test suite for CourseAttributeRepository."""

    async def test_save_new_attribute(
        self, course_attribute_repository: CourseAttributeRepository
    ):
        """Test saving a new course attribute."""
        attribute = CourseAttribute(
            id=None,
            name="General Education",
            degree_works_label="GE",
            courses_at_slu_label="General Ed",
        )

        saved = await course_attribute_repository.save(attribute)

        assert saved.id is not None
        assert saved.name == "General Education"
        assert saved.degree_works_label == "GE"
        assert saved.courses_at_slu_label == "General Ed"

    async def test_save_and_update_attribute(
        self, course_attribute_repository: CourseAttributeRepository
    ):
        """Test saving and then updating an attribute."""
        # Create and save a new attribute
        attribute = CourseAttribute(
            id=None,
            name="Core Requirement",
            degree_works_label="CORE",
            courses_at_slu_label="Core",
        )
        saved = await course_attribute_repository.save(attribute)
        attr_id = saved.id

        # Update the attribute
        updated_attribute = CourseAttribute(
            id=attr_id,
            name="Core Requirement - Updated",
            degree_works_label="CORE-UPD",
            courses_at_slu_label="Core Updated",
        )
        result = await course_attribute_repository.save(updated_attribute)

        assert result.id == attr_id
        assert result.name == "Core Requirement - Updated"

    async def test_get_by_id(
        self, course_attribute_repository: CourseAttributeRepository
    ):
        """Test retrieving an attribute by ID."""
        # Save an attribute
        attribute = CourseAttribute(
            id=None,
            name="Elective",
            degree_works_label="ELEC",
            courses_at_slu_label="Elective",
        )
        saved = await course_attribute_repository.save(attribute)
        assert saved.id is not None

        # Retrieve it
        retrieved = await course_attribute_repository.get_by_id(saved.id)

        assert retrieved is not None
        assert retrieved.id == saved.id
        assert retrieved.name == "Elective"
        assert retrieved.degree_works_label == "ELEC"

    async def test_get_by_id_not_found(
        self, course_attribute_repository: CourseAttributeRepository
    ):
        """Test retrieving a non-existent attribute raises ValueError."""
        with pytest.raises(ValueError):
            await course_attribute_repository.get_by_id(9999)
