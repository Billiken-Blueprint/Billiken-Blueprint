import pytest
from billiken_blueprint.repositories.course_repository import CourseRepository
from billiken_blueprint.domain.courses.course import Course


@pytest.mark.asyncio
class TestCourseRepository:
    """Test suite for CourseRepository."""

    async def test_save_new_course(self, course_repository: CourseRepository):
        """Test saving a new course to the database."""
        course = Course(
            id=None,
            major_code="CSCI",
            course_number="1000",
            attribute_ids=[1, 2],
            prerequisites=None,
        )

        saved_course = await course_repository.save(course)

        assert saved_course.id is not None
        assert saved_course.major_code == "CSCI"
        assert saved_course.course_number == "1000"
        assert saved_course.attribute_ids == [1, 2]
        assert saved_course.prerequisites is None

    async def test_save_and_update_course(self, course_repository: CourseRepository):
        """Test saving and then updating a course."""
        # Create and save a new course
        course = Course(
            id=None,
            major_code="CSCI",
            course_number="2000",
            attribute_ids=[1],
            prerequisites=None,
        )
        saved_course = await course_repository.save(course)
        course_id = saved_course.id

        # Update the course
        updated_course = Course(
            id=course_id,
            major_code="CSCI",
            course_number="2000",
            attribute_ids=[1, 2, 3],
            prerequisites=None,
        )
        result = await course_repository.save(updated_course)

        assert result.id == course_id
        assert result.attribute_ids == [1, 2, 3]

    async def test_get_by_id(self, course_repository: CourseRepository):
        """Test retrieving a course by ID."""
        # Save a course first
        course = Course(
            id=None,
            major_code="MATH",
            course_number="1500",
            attribute_ids=[2, 3],
            prerequisites=None,
        )
        saved_course = await course_repository.save(course)
        assert saved_course.id is not None

        # Retrieve it
        retrieved = await course_repository.get_by_id(saved_course.id)

        assert retrieved is not None
        assert retrieved.id == saved_course.id
        assert retrieved.major_code == "MATH"
        assert retrieved.course_number == "1500"
        assert retrieved.attribute_ids == [2, 3]

    async def test_get_by_id_not_found(self, course_repository: CourseRepository):
        """Test retrieving a non-existent course returns None."""
        result = await course_repository.get_by_id(9999)
        assert result is None

    async def test_get_all_empty(self, course_repository: CourseRepository):
        """Test getting all courses when database is empty."""
        courses = await course_repository.get_all()
        assert courses == []

    async def test_get_all_multiple_courses(self, course_repository: CourseRepository):
        """Test retrieving all courses when multiple exist."""
        # Save multiple courses
        course1 = Course(
            id=None,
            major_code="CSCI",
            course_number="1000",
            attribute_ids=[1],
            prerequisites=None,
        )
        course2 = Course(
            id=None,
            major_code="MATH",
            course_number="1500",
            attribute_ids=[2],
            prerequisites=None,
        )
        course3 = Course(
            id=None,
            major_code="PHYS",
            course_number="2000",
            attribute_ids=[3],
            prerequisites=None,
        )

        await course_repository.save(course1)
        await course_repository.save(course2)
        await course_repository.save(course3)

        # Get all courses
        all_courses = await course_repository.get_all()

        assert len(all_courses) == 3
        assert all(isinstance(c, Course) for c in all_courses)
        major_codes = [c.major_code for c in all_courses]
        assert "CSCI" in major_codes
        assert "MATH" in major_codes
        assert "PHYS" in major_codes

    async def test_save_course_with_prerequisites(
        self, course_repository: CourseRepository
    ):
        """Test saving a course with prerequisites."""
        from billiken_blueprint.domain.courses.course_prerequisite import (
            CourseCoursePrerequisite,
            NestedCoursePrerequisite,
        )

        # Create a nested prerequisite with a single course requirement
        prerequisite = NestedCoursePrerequisite(
            operator="AND",
            operands=[
                CourseCoursePrerequisite(
                    major_code="CSCI",
                    course_number="1000",
                    end_number=None,
                    concurrent_allowed=False,
                )
            ],
        )
        course = Course(
            id=None,
            major_code="CSCI",
            course_number="2100",
            attribute_ids=[1],
            prerequisites=prerequisite,
        )

        saved = await course_repository.save(course)
        assert saved.id is not None
        retrieved = await course_repository.get_by_id(saved.id)

        assert retrieved is not None
        assert retrieved.prerequisites is not None
