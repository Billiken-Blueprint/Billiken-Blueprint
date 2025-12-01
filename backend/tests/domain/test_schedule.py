import pytest
from billiken_blueprint.domain.section import Section, MeetingTime
from billiken_blueprint.domain.degrees.degree import Degree
from billiken_blueprint.domain.courses.course import CourseWithAttributes
from billiken_blueprint.domain.degrees.degree_requirement import DegreeRequirement, CourseRule, CourseWithCode

class TestSchedule:
    def test_meeting_time_overlaps(self):
        # Overlapping times on same day
        mt1 = MeetingTime(day=1, start_time="1000", end_time="1100")
        mt2 = MeetingTime(day=1, start_time="1030", end_time="1130")
        assert mt1.overlaps(mt2)
        assert mt2.overlaps(mt1)

        # Non-overlapping times on same day
        mt3 = MeetingTime(day=1, start_time="1100", end_time="1200")
        assert not mt1.overlaps(mt3) # 1100 end vs 1100 start - assuming exclusive end
        
        # Times on different days
        mt4 = MeetingTime(day=2, start_time="1000", end_time="1100")
        assert not mt1.overlaps(mt4)

    def test_section_overlaps(self):
        mt1 = MeetingTime(day=1, start_time="1000", end_time="1100")
        mt2 = MeetingTime(day=1, start_time="1030", end_time="1130")
        mt3 = MeetingTime(day=2, start_time="1000", end_time="1100")

        s1 = Section(
            id=1, crn="1", instructor_names=[], campus_code="STL", description="", title="S1",
            course_code="C1", semester="Fall", meeting_times=[mt1]
        )
        s2 = Section(
            id=2, crn="2", instructor_names=[], campus_code="STL", description="", title="S2",
            course_code="C2", semester="Fall", meeting_times=[mt2]
        )
        s3 = Section(
            id=3, crn="3", instructor_names=[], campus_code="STL", description="", title="S3",
            course_code="C3", semester="Fall", meeting_times=[mt3]
        )

        assert s1.overlaps(s2)
        assert not s1.overlaps(s3)

    def test_get_schedule(self):
        # Setup courses
        c1 = CourseWithAttributes(id=1, major_code="CSCI", course_number="1000", attribute_ids=[], prerequisites=None, attributes=[])
        c2 = CourseWithAttributes(id=2, major_code="CSCI", course_number="2000", attribute_ids=[], prerequisites=None, attributes=[])
        
        all_courses = [c1, c2]

        # Setup sections
        # S1 and S2 overlap
        mt1 = MeetingTime(day=1, start_time="1000", end_time="1100")
        mt2 = MeetingTime(day=1, start_time="1030", end_time="1130")
        
        s1 = Section(
            id=1, crn="1", instructor_names=[], campus_code="STL", description="", title="S1",
            course_code="CSCI 1000", semester="Fall", meeting_times=[mt1]
        )
        s2 = Section(
            id=2, crn="2", instructor_names=[], campus_code="STL", description="", title="S2",
            course_code="CSCI 2000", semester="Fall", meeting_times=[mt2]
        )
        
        all_sections = [s1, s2]

        # Setup Degree
        req = DegreeRequirement(
            label="Req", needed=2,
            course_rules=CourseRule(
                courses=[
                    CourseWithCode("CSCI", "1000"),
                    CourseWithCode("CSCI", "2000")
                ],
                exclude=[]
            )
        )
        degree = Degree(
            id=1, name="CS", degree_works_major_code="CS", degree_works_degree_type="BS",
            degree_works_college_code="ENGI", requirements=[req]
        )

        # Should only pick one because they overlap
        schedule = degree.get_schedule(
            taken_courses=[],
            all_courses=all_courses,
            all_sections=all_sections,
            course_equivalencies=[]
        )
        
        assert len(schedule) == 1
        assert schedule[0].section.crn == "1" # S1 comes first in recommendation (based on course order/score)

    def test_get_schedule_no_duplicates(self):
        # Setup courses
        c1 = CourseWithAttributes(id=1, major_code="CSCI", course_number="1000", attribute_ids=[], prerequisites=None, attributes=[])
        all_courses = [c1]

        # Setup sections: Two sections for the same course, non-overlapping
        mt1 = MeetingTime(day=1, start_time="1000", end_time="1100")
        mt2 = MeetingTime(day=1, start_time="1200", end_time="1300")
        
        s1 = Section(
            id=1, crn="1", instructor_names=[], campus_code="STL", description="", title="S1",
            course_code="CSCI 1000", semester="Fall", meeting_times=[mt1]
        )
        s2 = Section(
            id=2, crn="2", instructor_names=[], campus_code="STL", description="", title="S2",
            course_code="CSCI 1000", semester="Fall", meeting_times=[mt2]
        )
        
        all_sections = [s1, s2]

        # Setup Degree
        req = DegreeRequirement(
            label="Req", needed=1,
            course_rules=CourseRule(
                courses=[CourseWithCode("CSCI", "1000")],
                exclude=[]
            )
        )
        degree = Degree(
            id=1, name="CS", degree_works_major_code="CS", degree_works_degree_type="BS",
            degree_works_college_code="ENGI", requirements=[req]
        )

        schedule = degree.get_schedule(
            taken_courses=[],
            all_courses=all_courses,
            all_sections=all_sections,
            course_equivalencies=[]
        )
        
        # Should only pick one even though they don't overlap, because they are the same course
        assert len(schedule) == 1
        assert schedule[0].section.crn == "1"

    def test_get_schedule_avoids_overmeeting(self):
        # Setup courses
        c1 = CourseWithAttributes(id=1, major_code="CSCI", course_number="1000", attribute_ids=[], prerequisites=None, attributes=[])
        c2 = CourseWithAttributes(id=2, major_code="CSCI", course_number="2000", attribute_ids=[], prerequisites=None, attributes=[])
        c3 = CourseWithAttributes(id=3, major_code="CSCI", course_number="3000", attribute_ids=[], prerequisites=None, attributes=[])
        all_courses = [c1, c2, c3]

        # Setup sections: all non-overlapping
        mt1 = MeetingTime(day=1, start_time="1000", end_time="1100")
        mt2 = MeetingTime(day=1, start_time="1200", end_time="1300")
        mt3 = MeetingTime(day=1, start_time="1400", end_time="1500")
        
        s1 = Section(
            id=1, crn="1", instructor_names=[], campus_code="STL", description="", title="S1",
            course_code="CSCI 1000", semester="Fall", meeting_times=[mt1]
        )
        s2 = Section(
            id=2, crn="2", instructor_names=[], campus_code="STL", description="", title="S2",
            course_code="CSCI 2000", semester="Fall", meeting_times=[mt2]
        )
        s3 = Section(
            id=3, crn="3", instructor_names=[], campus_code="STL", description="", title="S3",
            course_code="CSCI 3000", semester="Fall", meeting_times=[mt3]
        )
        
        all_sections = [s1, s2, s3]

        # Setup Degree: Requirement needs 2 courses. 3 available.
        req = DegreeRequirement(
            label="Req", needed=2,
            course_rules=CourseRule(
                courses=[
                    CourseWithCode("CSCI", "1000"),
                    CourseWithCode("CSCI", "2000"),
                    CourseWithCode("CSCI", "3000")
                ],
                exclude=[]
            )
        )
        degree = Degree(
            id=1, name="CS", degree_works_major_code="CS", degree_works_degree_type="BS",
            degree_works_college_code="ENGI", requirements=[req]
        )

        # Scenario 1: No courses taken. Should pick 2.
        schedule = degree.get_schedule(
            taken_courses=[],
            all_courses=all_courses,
            all_sections=all_sections,
            course_equivalencies=[]
        )
        assert len(schedule) == 2

        # Scenario 2: One course taken. Should pick 1.
        schedule = degree.get_schedule(
            taken_courses=[c1],
            all_courses=all_courses,
            all_sections=all_sections,
            course_equivalencies=[]
        )
        assert len(schedule) == 1
        assert schedule[0].section.course_code != "CSCI 1000" # Should not pick the taken one (filtered by get_recommended_sections)

    def test_get_schedule_dynamic_scoring(self):
        # Setup courses
        # C1: A, B
        # C2: A, C
        # C3: B, C
        # Requirements: A, B, C
        # If we pick C1 (A, B), we still need C.
        # C2 provides C (and A). C3 provides C (and B).
        # Both are equal in "marginal utility" (1 new requirement).
        
        # Better Scenario:
        # Req: A, B, C, D
        # C1: A, B, C
        # C2: A, B, D
        # C3: D, E (Let's say E is also needed)
        
        c1 = CourseWithAttributes(id=1, major_code="TEST", course_number="100", attribute_ids=[], prerequisites=None, attributes=[])
        c2 = CourseWithAttributes(id=2, major_code="TEST", course_number="200", attribute_ids=[], prerequisites=None, attributes=[])
        c3 = CourseWithAttributes(id=3, major_code="TEST", course_number="300", attribute_ids=[], prerequisites=None, attributes=[])
        all_courses = [c1, c2, c3]

        mt1 = MeetingTime(day=1, start_time="1000", end_time="1100")
        mt2 = MeetingTime(day=1, start_time="1200", end_time="1300")
        mt3 = MeetingTime(day=1, start_time="1400", end_time="1500")

        s1 = Section(id=1, crn="1", instructor_names=[], campus_code="STL", description="", title="S1", course_code="TEST 100", semester="Fall", meeting_times=[mt1])
        s2 = Section(id=2, crn="2", instructor_names=[], campus_code="STL", description="", title="S2", course_code="TEST 200", semester="Fall", meeting_times=[mt2])
        s3 = Section(id=3, crn="3", instructor_names=[], campus_code="STL", description="", title="S3", course_code="TEST 300", semester="Fall", meeting_times=[mt3])
        
        # Ensure static order is S1, S2, S3 (by making S2 score higher than S3 initially if needed, or just relying on list order if scores are equal)
        # We'll rely on list order if scores are equal.
        all_sections = [s1, s2, s3]

        req_a = DegreeRequirement(label="A", needed=1, course_rules=CourseRule(courses=[CourseWithCode("TEST", "100"), CourseWithCode("TEST", "200")], exclude=[]))
        req_b = DegreeRequirement(label="B", needed=1, course_rules=CourseRule(courses=[CourseWithCode("TEST", "100"), CourseWithCode("TEST", "200")], exclude=[]))
        req_c = DegreeRequirement(label="C", needed=1, course_rules=CourseRule(courses=[CourseWithCode("TEST", "100")], exclude=[]))
        req_d = DegreeRequirement(label="D", needed=1, course_rules=CourseRule(courses=[CourseWithCode("TEST", "200"), CourseWithCode("TEST", "300")], exclude=[]))
        req_e = DegreeRequirement(label="E", needed=1, course_rules=CourseRule(courses=[CourseWithCode("TEST", "300")], exclude=[]))

        # C1 satisfies A, B, C
        # C2 satisfies A, B, D
        # C3 satisfies D, E
        
        degree = Degree(
            id=1, name="Test", degree_works_major_code="T", degree_works_degree_type="BS", degree_works_college_code="T",
            requirements=[req_a, req_b, req_c, req_d, req_e]
        )

        # With static greedy (assuming order S1, S2, S3):
        # 1. Pick S1. Satisfies A, B, C. Remaining: D, E.
        # 2. Consider S2. Satisfies D (useful). Pick S2. Satisfies A, B (redundant), D. Remaining: E.
        # 3. Consider S3. Satisfies D (redundant), E (useful). Pick S3.
        # Result: S1, S2, S3. (3 courses)
        
        # With dynamic greedy:
        # 1. Pick S1 (score 3: A,B,C). Remaining: D, E.
        # 2. Re-score:
        #    S2: Satisfies D. Score = 1.
        #    S3: Satisfies D, E. Score = 2.
        # 3. Pick S3. Satisfies D, E. Remaining: None.
        # Result: S1, S3. (2 courses)

        schedule = degree.get_schedule(
            taken_courses=[],
            all_courses=all_courses,
            all_sections=all_sections,
            course_equivalencies=[]
        )

        # We want the optimized schedule
        assert len(schedule) == 2
        assert any(s.section.course_code == "TEST 100" for s in schedule)
        assert any(s.section.course_code == "TEST 300" for s in schedule)

    def test_get_schedule_includes_high_level_non_major_if_needed(self):
        # Setup courses
        # Major is "CSCI"
        # C1: CSCI 3000 (Should be allowed)
        # C2: HIST 3000 (Should be filtered out)
        # C3: HIST 1000 (Should be allowed)
        
        c1 = CourseWithAttributes(id=1, major_code="CSCI", course_number="3000", attribute_ids=[], prerequisites=None, attributes=[])
        c2 = CourseWithAttributes(id=2, major_code="HIST", course_number="3000", attribute_ids=[], prerequisites=None, attributes=[])
        c3 = CourseWithAttributes(id=3, major_code="HIST", course_number="1000", attribute_ids=[], prerequisites=None, attributes=[])
        all_courses = [c1, c2, c3]

        mt1 = MeetingTime(day=1, start_time="1000", end_time="1100")
        mt2 = MeetingTime(day=1, start_time="1200", end_time="1300")
        mt3 = MeetingTime(day=1, start_time="1400", end_time="1500")

        s1 = Section(id=1, crn="1", instructor_names=[], campus_code="STL", description="", title="S1", course_code="CSCI 3000", semester="Fall", meeting_times=[mt1])
        s2 = Section(id=2, crn="2", instructor_names=[], campus_code="STL", description="", title="S2", course_code="HIST 3000", semester="Fall", meeting_times=[mt2])
        s3 = Section(id=3, crn="3", instructor_names=[], campus_code="STL", description="", title="S3", course_code="HIST 1000", semester="Fall", meeting_times=[mt3])
        
        all_sections = [s1, s2, s3]

        # Requirement that allows all of them
        req = DegreeRequirement(
            label="Req", needed=3,
            course_rules=CourseRule(
                courses=[
                    CourseWithCode("CSCI", "3000"),
                    CourseWithCode("HIST", "3000"),
                    CourseWithCode("HIST", "1000")
                ],
                exclude=[]
            )
        )
        
        degree = Degree(
            id=1, name="CS", degree_works_major_code="CS", degree_works_degree_type="BS", degree_works_college_code="ENGI",
            requirements=[req]
        )

        schedule = degree.get_schedule(
            taken_courses=[],
            all_courses=all_courses,
            all_sections=all_sections,
            course_equivalencies=[]
        )

        # Should contain CSCI 3000 and HIST 1000.
        # HIST 3000 should also be included because we need 3 courses and only 3 are available.
        # However, it should be deprioritized (lowest score).
        course_codes = [s.section.course_code for s in schedule]
        assert "CSCI 3000" in course_codes
        assert "HIST 1000" in course_codes
        assert "HIST 3000" in course_codes
        assert len(schedule) == 3

    def test_get_schedule_deprioritizes_high_level_non_major(self):
        # Setup courses
        # Major is "CSCI"
        # C1: CSCI 3000 (Priority)
        # C2: HIST 3000 (Deprioritized)
        # C3: HIST 1000 (Priority)
        # C4: CSCI 1000 (Priority)
        
        c1 = CourseWithAttributes(id=1, major_code="CSCI", course_number="3000", attribute_ids=[], prerequisites=None, attributes=[])
        c2 = CourseWithAttributes(id=2, major_code="HIST", course_number="3000", attribute_ids=[], prerequisites=None, attributes=[])
        c3 = CourseWithAttributes(id=3, major_code="HIST", course_number="1000", attribute_ids=[], prerequisites=None, attributes=[])
        c4 = CourseWithAttributes(id=4, major_code="CSCI", course_number="1000", attribute_ids=[], prerequisites=None, attributes=[])
        all_courses = [c1, c2, c3, c4]

        mt1 = MeetingTime(day=1, start_time="1000", end_time="1100")
        mt2 = MeetingTime(day=1, start_time="1200", end_time="1300")
        mt3 = MeetingTime(day=1, start_time="1400", end_time="1500")
        mt4 = MeetingTime(day=1, start_time="1600", end_time="1700")

        s1 = Section(id=1, crn="1", instructor_names=[], campus_code="STL", description="", title="S1", course_code="CSCI 3000", semester="Fall", meeting_times=[mt1])
        s2 = Section(id=2, crn="2", instructor_names=[], campus_code="STL", description="", title="S2", course_code="HIST 3000", semester="Fall", meeting_times=[mt2])
        s3 = Section(id=3, crn="3", instructor_names=[], campus_code="STL", description="", title="S3", course_code="HIST 1000", semester="Fall", meeting_times=[mt3])
        s4 = Section(id=4, crn="4", instructor_names=[], campus_code="STL", description="", title="S4", course_code="CSCI 1000", semester="Fall", meeting_times=[mt4])
        
        all_sections = [s1, s2, s3, s4]

        # Requirement that allows all of them, but we only need 3
        req = DegreeRequirement(
            label="Req", needed=3,
            course_rules=CourseRule(
                courses=[
                    CourseWithCode("CSCI", "3000"),
                    CourseWithCode("HIST", "3000"),
                    CourseWithCode("HIST", "1000"),
                    CourseWithCode("CSCI", "1000")
                ],
                exclude=[]
            )
        )
        
        degree = Degree(
            id=1, name="CS", degree_works_major_code="CS", degree_works_degree_type="BS", degree_works_college_code="ENGI",
            requirements=[req]
        )

        schedule = degree.get_schedule(
            taken_courses=[],
            all_courses=all_courses,
            all_sections=all_sections,
            course_equivalencies=[]
        )

        # Should pick the 3 priority courses and skip HIST 3000
        course_codes = [s.section.course_code for s in schedule]
        assert "CSCI 3000" in course_codes
        assert "HIST 1000" in course_codes
        assert "CSCI 1000" in course_codes
        assert "HIST 3000" not in course_codes
        assert len(schedule) == 3
