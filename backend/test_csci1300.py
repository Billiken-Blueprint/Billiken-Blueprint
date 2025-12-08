"""
Test script to verify instructor ratings work for CSCI 1300 schedule generation.
This demonstrates that sections with higher-rated instructors are prioritized.
"""

from billiken_blueprint.domain.section import Section, MeetingTime
from billiken_blueprint.domain.degrees.degree import Degree
from billiken_blueprint.domain.courses.course import CourseWithAttributes
from billiken_blueprint.domain.degrees.degree_requirement import (
    DegreeRequirement,
    CourseRule,
    CourseWithCode,
)
from billiken_blueprint.domain.student import Student
from billiken_blueprint.use_cases.get_schedule import get_schedule


def test_csci_1300_instructor_ratings():
    """Test that CSCI 1300 sections with higher-rated instructors are prioritized."""
    print("=" * 80)
    print("Testing CSCI 1300 Schedule Generation with Instructor Ratings")
    print("=" * 80)
    
    # Setup course
    csci_1300 = CourseWithAttributes(
        id=1,
        major_code="CSCI",
        course_number="1300",
        attribute_ids=[],
        prerequisites=None,
        attributes=[],
    )
    all_courses = [csci_1300]

    # Setup sections: Multiple sections for CSCI 1300 with different instructors
    # Based on real data: David Letscher (2.7 rating) and Michael Liljegren (4.4 rating)
    mt1 = MeetingTime(day=1, start_time="1000", end_time="1050")  # MWF 10:00-10:50
    mt2 = MeetingTime(day=1, start_time="1100", end_time="1150")  # MWF 11:00-11:50
    
    section_letscher = Section(
        id=1,
        crn="20235",
        instructor_names=["David Letscher"],
        campus_code="North Campus (Main Campus)",
        description="Introduction to Object-Oriented Programming",
        title="CSCI 1300",
        course_code="CSCI 1300",
        semester="202501",
        meeting_times=[mt1],
    )
    
    section_liljegren = Section(
        id=2,
        crn="20236",
        instructor_names=["Michael Liljegren"],
        campus_code="North Campus (Main Campus)",
        description="Introduction to Object-Oriented Programming",
        title="CSCI 1300",
        course_code="CSCI 1300",
        semester="202501",
        meeting_times=[mt2],
    )
    
    all_sections = [section_letscher, section_liljegren]

    # Setup Degree requirement
    req = DegreeRequirement(
        label="Core Programming",
        needed=1,
        course_rules=CourseRule(
            courses=[CourseWithCode("CSCI", "1300")],
            exclude=[],
        ),
    )
    degree = Degree(
        id=1,
        name="Computer Science",
        degree_works_major_code="CS",
        degree_works_degree_type="BS",
        degree_works_college_code="ENGI",
        requirements=[req],
    )

    # Create instructor ratings map based on RateMyProfessor data
    # David Letscher: 2.7 rating (52 reviews)
    # Michael Liljegren: 4.4 rating (7 reviews)
    instructor_ratings_map = {
        "David Letscher": 2.7,
        "david letscher": 2.7,  # lowercase for case-insensitive matching
        "Michael Liljegren": 4.4,
        "michael liljegren": 4.4,
    }

    print("\nTest Setup:")
    print(f"  Course: CSCI 1300")
    print(f"  Section 1 (CRN 20235): David Letscher (Rating: 2.7)")
    print(f"  Section 2 (CRN 20236): Michael Liljegren (Rating: 4.4)")
    print(f"\nExpected Result: Section with Michael Liljegren should be prioritized")
    print("-" * 80)

    # Test WITHOUT instructor ratings (baseline)
    print("\n1. Testing WITHOUT instructor ratings:")
    schedule_no_ratings = get_schedule(
        degree=degree,
        student=Student(
            id=1,
            name="Test Student",
            degree_id=1,
            graduation_year=2025,
            completed_course_ids=[],
            desired_course_ids=[],
            unavailability_times=[],
            avoid_times=[],
        ),
        taken_courses=[],
        all_courses=all_courses,
        all_sections=all_sections,
        course_equivalencies=[],
        instructor_ratings_map=None,  # No ratings
    )

    print(f"   Selected section: CRN {schedule_no_ratings[0].section.crn}")
    print(f"   Instructor: {schedule_no_ratings[0].section.instructor_names[0]}")

    # Test WITH instructor ratings
    print("\n2. Testing WITH instructor ratings:")
    schedule_with_ratings = get_schedule(
        degree=degree,
        student=Student(
            id=1,
            name="Test Student",
            degree_id=1,
            graduation_year=2025,
            completed_course_ids=[],
            desired_course_ids=[],
            unavailability_times=[],
            avoid_times=[],
        ),
        taken_courses=[],
        all_courses=all_courses,
        all_sections=all_sections,
        course_equivalencies=[],
        instructor_ratings_map=instructor_ratings_map,
    )

    print(f"   Selected section: CRN {schedule_with_ratings[0].section.crn}")
    print(f"   Instructor: {schedule_with_ratings[0].section.instructor_names[0]}")

    # Verify results
    print("\n" + "=" * 80)
    print("Test Results:")
    print("=" * 80)
    
    selected_crn = schedule_with_ratings[0].section.crn
    selected_instructor = schedule_with_ratings[0].section.instructor_names[0]
    
    if selected_crn == "20236" and selected_instructor == "Michael Liljegren":
        print("✅ PASS: Higher-rated instructor (Michael Liljegren, 4.4) was selected")
        print(f"   - Selected CRN: {selected_crn}")
        print(f"   - Selected Instructor: {selected_instructor}")
        print(f"   - Instructor Rating: 4.4")
        return True
    else:
        print("❌ FAIL: Expected Michael Liljegren's section to be selected")
        print(f"   - Selected CRN: {selected_crn}")
        print(f"   - Selected Instructor: {selected_instructor}")
        return False


if __name__ == "__main__":
    success = test_csci_1300_instructor_ratings()
    exit(0 if success else 1)

