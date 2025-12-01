import pytest
from billiken_blueprint.domain.degrees.degree import Degree
from billiken_blueprint.domain.courses.course import CourseWithAttributes, Course
from billiken_blueprint.domain.section import Section, MeetingTime
from billiken_blueprint.domain.degrees.degree_requirement import DegreeRequirement, CourseRule, CourseWithCode
from billiken_blueprint.domain.courses.course_prerequisite import CourseCoursePrerequisite, NestedCoursePrerequisite

class TestDegree:
    def test_get_recommended_sections_filters_permissions(self):
        # Setup courses
        # Course 1: No prereqs
        c1 = CourseWithAttributes(
            id=1, major_code="CSCI", course_number="1000", attribute_ids=[], prerequisites=None, attributes=[]
        )
        # Course 2: Prereq is C1
        c2_prereq_leaf = CourseCoursePrerequisite(major_code="CSCI", course_number="1000", end_number=None, concurrent_allowed=False)
        c2_prereq = NestedCoursePrerequisite(operator="AND", operands=[c2_prereq_leaf])
        c2 = CourseWithAttributes(
            id=2, major_code="CSCI", course_number="2000", attribute_ids=[], prerequisites=c2_prereq, attributes=[]
        )
        # Course 3: Prereq is C2
        c3_prereq_leaf = CourseCoursePrerequisite(major_code="CSCI", course_number="2000", end_number=None, concurrent_allowed=False)
        c3_prereq = NestedCoursePrerequisite(operator="AND", operands=[c3_prereq_leaf])
        c3 = CourseWithAttributes(
            id=3, major_code="CSCI", course_number="3000", attribute_ids=[], prerequisites=c3_prereq, attributes=[]
        )

        all_courses = [c1, c2, c3]

        # Setup sections
        s1 = Section(
            id=1, crn="1", instructor_names=[], campus_code="STL", description="", title="Intro",
            course_code="CSCI 1000", semester="Fall 2023", meeting_times=[]
        )
        s2 = Section(
            id=2, crn="2", instructor_names=[], campus_code="STL", description="", title="Inter",
            course_code="CSCI 2000", semester="Fall 2023", meeting_times=[]
        )
        s3 = Section(
            id=3, crn="3", instructor_names=[], campus_code="STL", description="", title="Adv",
            course_code="CSCI 3000", semester="Fall 2023", meeting_times=[]
        )
        all_sections = [s1, s2, s3]

        # Setup Degree with requirements for all 3 courses
        req = DegreeRequirement(
            label="CS Core",
            needed=3,
            course_rules=CourseRule(
                courses=[
                    CourseWithCode("CSCI", "1000"),
                    CourseWithCode("CSCI", "2000"),
                    CourseWithCode("CSCI", "3000"),
                ],
                exclude=[]
            )
        )
        degree = Degree(
            id=1, name="CS", degree_works_major_code="CS", degree_works_degree_type="BS",
            degree_works_college_code="ENGI", requirements=[req]
        )

        # Case 1: No courses taken. Should only recommend C1 (s1).
        # C2 requires C1 (not taken). C3 requires C2 (not taken).
        recs = degree.get_recommended_sections(
            taken_courses=[],
            all_courses=all_courses,
            all_sections=all_sections,
            course_equivalencies=[]
        )
        rec_crns = [r.section.crn for r in recs]
        assert "1" in rec_crns
        assert "2" not in rec_crns
        assert "3" not in rec_crns

        # Case 2: C1 taken. Should recommend C2 (s2).
        # C1 already taken, so s1 should be filtered out.
        # C2 prereq (C1) satisfied.
        # C3 prereq (C2) not satisfied.
        recs = degree.get_recommended_sections(
            taken_courses=[c1],
            all_courses=all_courses,
            all_sections=all_sections,
            course_equivalencies=[]
        )
        rec_crns = [r.section.crn for r in recs]
        assert "1" not in rec_crns
        assert "2" in rec_crns
        assert "3" not in rec_crns
