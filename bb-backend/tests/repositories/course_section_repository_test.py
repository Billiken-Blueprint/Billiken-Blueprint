import pytest
import pytest_asyncio
from sqlalchemy import select

from billiken_blueprint.courses_at_slu.section import Section, MeetingTime
from billiken_blueprint.domain.instructor import Professor
from billiken_blueprint.repositories.course_section_repository import (
    CourseSectionRepository,
)
from billiken_blueprint.repositories.instructor_repository import (
    InstructorRepository,
)


@pytest_asyncio.fixture
async def course_section_repository(async_sessionmaker):
    """Create a CourseSectionRepository instance."""
    return CourseSectionRepository(async_sessionmaker)


@pytest_asyncio.fixture
async def instructor_repository(async_sessionmaker):
    """Create an InstructorRepository instance."""
    return InstructorRepository(async_sessionmaker)


@pytest.mark.asyncio
async def test_save_section_with_persisted_instructors(
    course_section_repository, instructor_repository
):
    """Test the flow: create instructor objects, persist them, then populate and persist section with returned IDs."""
    # Arrange - create instructor domain objects
    instructor_objects = [
        Professor(id=None, name="Dr. Smith"),
        Professor(id=None, name="Dr. Johnson"),
    ]

    # Act - persist instructors and collect their returned IDs
    persisted_instructors = []
    for instructor in instructor_objects:
        persisted_instructor = await instructor_repository.save(instructor)
        persisted_instructors.append(persisted_instructor)

    # Extract IDs from persisted instructors
    instructor_ids = [inst.id for inst in persisted_instructors]

    # Create and save section with the persisted instructor IDs
    section = Section(
        meeting_times=[MeetingTime(day=1, start_time="09:00", end_time="10:30")],
        instructor_names=["Dr. Smith", "Dr. Johnson"],
        campus_code="MAIN",
        description="Intro to CS",
        title="CS 101",
    )
    saved_section = await course_section_repository.save(
        section, course_id=1, crn="12345", instructor_ids=instructor_ids
    )

    # Assert - verify the section and instructors are persisted
    assert saved_section.id is not None
    assert saved_section.course_id == 1
    assert saved_section.crn == "12345"
    assert len(instructor_ids) == 2
    assert all(id is not None for id in instructor_ids)

    # Query the instructors by name to verify they were persisted correctly
    for original_instructor, persisted_instructor in zip(
        instructor_objects, persisted_instructors
    ):
        queried_instructor = await instructor_repository.get_by_name(
            original_instructor.name
        )
        assert queried_instructor is not None
        assert queried_instructor.id == persisted_instructor.id
        assert queried_instructor.name == original_instructor.name
