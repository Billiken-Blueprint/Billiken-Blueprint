import pytest
import os
import json
import tempfile
from pathlib import Path
from billiken_blueprint.repositories.section_repository import SectionRepository
from billiken_blueprint.domain.section import Section, MeetingTime


@pytest.mark.asyncio
class TestSectionRepository:
    """Test suite for SectionRepository."""

    async def test_save_new_section(self, section_repository: SectionRepository):
        """Test saving a new section to the database."""
        section = Section(
            id=None,
            crn="12345",
            instructor_names=["Dr. Smith", "Dr. Jones"],
            campus_code="MAIN",
            description="Introduction to Computer Science",
            title="CSCI 1000",
            course_code="CSCI-1000",
            semester="Fall 2024",
            meeting_times=[
                MeetingTime(day=0, start_time="09:00", end_time="09:50"),
                MeetingTime(day=2, start_time="10:00", end_time="10:50"),
            ],
        )

        saved = await section_repository.save(section)

        assert saved.id is not None
        assert saved.crn == "12345"
        assert saved.course_code == "CSCI-1000"
        assert len(saved.meeting_times) == 2

    async def test_save_and_update_section(self, section_repository: SectionRepository):
        """Test saving and then updating a section."""
        # Create and save a new section
        section = Section(
            id=None,
            crn="54321",
            instructor_names=["Dr. Brown"],
            campus_code="NORTH",
            description="Data Structures",
            title="CSCI 2100",
            course_code="CSCI-2100",
            semester="Spring 2024",
            meeting_times=[MeetingTime(day=1, start_time="11:00", end_time="12:15")],
        )
        saved = await section_repository.save(section)
        section_id = saved.id

        # Update the section
        updated_section = Section(
            id=section_id,
            crn="54321",
            instructor_names=["Dr. Brown", "Dr. White"],
            campus_code="NORTH",
            description="Data Structures",
            title="CSCI 2100",
            course_code="CSCI-2100",
            semester="Spring 2024",
            meeting_times=[MeetingTime(day=1, start_time="14:00", end_time="15:15")],
        )
        result = await section_repository.save(updated_section)

        assert result.id == section_id
        assert len(result.instructor_names) == 2

    async def test_get_all_empty(self, section_repository: SectionRepository):
        """Test getting all sections when database is empty."""
        sections = await section_repository.get_all()
        assert sections == []

    async def test_get_all_multiple_sections(
        self, section_repository: SectionRepository
    ):
        """Test retrieving all sections when multiple exist."""
        # Save multiple sections
        section1 = Section(
            id=None,
            crn="11111",
            instructor_names=["Dr. A"],
            campus_code="MAIN",
            description="Intro to CS",
            title="CSCI 1000",
            course_code="CSCI-1000",
            semester="Fall 2024",
            meeting_times=[MeetingTime(day=0, start_time="09:00", end_time="09:50")],
        )
        section2 = Section(
            id=None,
            crn="22222",
            instructor_names=["Dr. B"],
            campus_code="SOUTH",
            description="Web Development",
            title="CSCI 3400",
            course_code="CSCI-3400",
            semester="Spring 2024",
            meeting_times=[MeetingTime(day=1, start_time="14:00", end_time="15:15")],
        )

        await section_repository.save(section1)
        await section_repository.save(section2)

        # Get all sections
        all_sections = await section_repository.get_all()

        assert len(all_sections) == 2
        assert all(isinstance(s, Section) for s in all_sections)

    async def test_get_all_for_semester(self, section_repository: SectionRepository):
        """Test retrieving sections for a specific semester."""
        # Save sections in different semesters
        fall_section = Section(
            id=None,
            crn="33333",
            instructor_names=["Dr. C"],
            campus_code="MAIN",
            description="Algorithms",
            title="CSCI 3100",
            course_code="CSCI-3100",
            semester="Fall 2024",
            meeting_times=[MeetingTime(day=0, start_time="10:00", end_time="10:50")],
        )
        spring_section = Section(
            id=None,
            crn="44444",
            instructor_names=["Dr. D"],
            campus_code="MAIN",
            description="Databases",
            title="CSCI 4300",
            course_code="CSCI-4300",
            semester="Spring 2025",
            meeting_times=[MeetingTime(day=1, start_time="11:00", end_time="12:15")],
        )

        await section_repository.save(fall_section)
        await section_repository.save(spring_section)

        # Get sections for Fall 2024
        fall_sections = await section_repository.get_all_for_semester("Fall 2024")
        assert len(fall_sections) == 1
        assert fall_sections[0].semester == "Fall 2024"

        # Get sections for Spring 2025
        spring_sections = await section_repository.get_all_for_semester("Spring 2025")
        assert len(spring_sections) == 1
        assert spring_sections[0].semester == "Spring 2025"

    async def test_get_by_course_code_and_semester(
        self, section_repository: SectionRepository
    ):
        """Test retrieving sections by course code and semester."""
        # Save sections with different course codes
        section1 = Section(
            id=None,
            crn="55555",
            instructor_names=["Dr. E"],
            campus_code="MAIN",
            description="Intro CS",
            title="CSCI 1000",
            course_code="CSCI-1000",
            semester="Fall 2024",
            meeting_times=[MeetingTime(day=0, start_time="09:00", end_time="09:50")],
        )
        section2 = Section(
            id=None,
            crn="66666",
            instructor_names=["Dr. F"],
            campus_code="MAIN",
            description="Intro CS - Lab",
            title="CSCI 1000L",
            course_code="CSCI-1000",
            semester="Fall 2024",
            meeting_times=[MeetingTime(day=3, start_time="14:00", end_time="16:00")],
        )
        section3 = Section(
            id=None,
            crn="77777",
            instructor_names=["Dr. G"],
            campus_code="MAIN",
            description="Intro CS",
            title="CSCI 1000",
            course_code="CSCI-1000",
            semester="Spring 2025",
            meeting_times=[MeetingTime(day=1, start_time="10:00", end_time="11:15")],
        )

        await section_repository.save(section1)
        await section_repository.save(section2)
        await section_repository.save(section3)

        # Get sections for CSCI-1000 in Fall 2024
        fall_sections = await section_repository.get_by_course_code_and_semester(
            "CSCI-1000", "Fall 2024"
        )
        assert len(fall_sections) == 2

        # Get sections for CSCI-1000 in Spring 2025
        spring_sections = await section_repository.get_by_course_code_and_semester(
            "CSCI-1000", "Spring 2025"
        )
        assert len(spring_sections) == 1
        assert spring_sections[0].semester == "Spring 2025"

    async def test_save_section_by_crn_and_semester_lookup(
        self, section_repository: SectionRepository
    ):
        """Test that save method can update sections by CRN and semester."""
        # Save initial section
        section = Section(
            id=None,
            crn="88888",
            instructor_names=["Dr. H"],
            campus_code="MAIN",
            description="Initial description",
            title="MATH 1500",
            course_code="MATH-1500",
            semester="Fall 2024",
            meeting_times=[MeetingTime(day=0, start_time="09:00", end_time="09:50")],
        )
        saved1 = await section_repository.save(section)
        original_id = saved1.id

        # Save same CRN and semester with updated data
        updated_section = Section(
            id=None,  # Intentionally None to test CRN lookup
            crn="88888",
            instructor_names=["Dr. H", "Dr. I"],
            campus_code="MAIN",
            description="Updated description",
            title="MATH 1500",
            course_code="MATH-1500",
            semester="Fall 2024",
            meeting_times=[MeetingTime(day=1, start_time="10:00", end_time="11:15")],
        )
        saved2 = await section_repository.save(updated_section)

        # Should be the same ID
        assert saved2.id == original_id
        assert len(saved2.instructor_names) == 2
