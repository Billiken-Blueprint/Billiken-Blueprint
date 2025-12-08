from typing import Sequence

from billiken_blueprint.domain.courses.course import CourseCode, CourseWithAttributes
from billiken_blueprint.domain.degrees.degree import (
    Degree,
    SectionWithRequirementsFulfilled,
    section_overlaps_timeslots,
)
from billiken_blueprint.domain.degrees.degree_requirement import (
    CourseRule,
    CourseWithCode,
    DegreeRequirement,
)
from billiken_blueprint.domain.section import Section
from billiken_blueprint.domain.student import Student, TimeSlot



def get_combined_requirements(
    degree: Degree,
    student: Student,
    all_courses: Sequence[CourseWithAttributes]
) -> Sequence[DegreeRequirement]:
    desired_reqs = []
    if student.desired_course_ids:
        # Create a map for quick course lookup
        all_courses_map = {c.id: c for c in all_courses}
        for course_id in student.desired_course_ids:
            if course_id in all_courses_map:
                course = all_courses_map[course_id]
                desired_reqs.append(
                    DegreeRequirement(
                        label=f"Desired: {course.major_code} {course.course_number}",
                        needed=1,
                        course_rules=CourseRule(
                            courses=[
                                CourseWithCode(
                                    major_code=course.major_code,
                                    course_number=course.course_number,
                                )
                            ],
                            exclude=[],
                        ),
                    )
                )
    return list(degree.requirements) + desired_reqs


def get_recommended_sections(
    degree: Degree,
    student: Student,
    taken_courses: Sequence[CourseWithAttributes],
    all_courses: Sequence[CourseWithAttributes],
    all_sections: Sequence[Section],
    course_equivalencies: Sequence[Sequence[CourseCode]],
    unavailability_times: Sequence[TimeSlot] = [],
    avoid_times: Sequence[TimeSlot] = [],
    instructor_ratings_map: dict[str, float] | None = None,
) -> Sequence[SectionWithRequirementsFulfilled]:
    # Same scoring mechanism as last implementation,
    # but this time we should first check which courses
    # satisfy degree requirements. Then we should traverse the
    # dependency tree to get all courses a part of the tree.
    # And we should add 1 to the score of that course.
    # This way, courses that are a part of more dependency
    # trees are prioritized first.
    # Then, we rank sections by the score of their courses.
    # Then, we can take N sections that haven't been taken yet
    # and have their course's requirements satisfied.

    # Parse equivalencies into a lookup map.
    equivalency_map = {}
    for i, equivalency_group in enumerate(course_equivalencies):
        for course_code in equivalency_group:
            equivalency_map[course_code] = i

    all_requirements = get_combined_requirements(degree, student, all_courses)

    # Get unfulfilled requirements.
    fulfilled_reqs = [
        c for c in all_requirements if c.is_satisfied_by(taken_courses)
    ]
    unfulfilled_reqs = [c for c in all_requirements if c not in fulfilled_reqs]

    # Score courses based on how many courses they are prerequisites for.
    course_scores = {}
    course_eq_scores = {}
    course_to_requirements = {}

    for req in unfulfilled_reqs:
        courses = req.filter_for_untaken_satisfying_courses(
            all_courses, taken_courses
        )
        for course in courses:
            if course not in course_to_requirements:
                course_to_requirements[course] = []
            course_to_requirements[course].append(req.label)

            if course.prerequisites is not None:
                for prereq in course.prerequisites.filter_for_satisfying_courses(
                    all_courses
                ):
                    course_scores[prereq] = course_scores.get(prereq, 0) + 1
                    if prereq in equivalency_map:
                        course_eq_scores[equivalency_map[prereq]] = (
                            course_eq_scores.get(equivalency_map[prereq], 0) + 1
                        )
            course_scores[course] = course_scores.get(course, 0) + 1
            if course in equivalency_map:
                course_eq_scores[equivalency_map[course]] = (
                    course_eq_scores.get(equivalency_map[course], 0) + 1
                )

    for code, group_num in equivalency_map.items():
        if group_num in course_eq_scores:
            course_scores[code] = course_eq_scores[group_num]

    if course_scores:
        max_score = max(course_scores.values())
        for course in course_scores:
            try:
                course_num = int(course.course_number.replace("X", ""))
                if course_num >= 3000 and course.major_code != degree.course_major_code:
                    course_scores[course] -= max_score
            except ValueError:
                pass

    # Score sections based on their course scores.
    course_codes_to_course = {
        f"{c.major_code} {c.course_number}": c for c in course_scores.keys()
    }
    sections = [
        section
        for section in all_sections
        if section.course_code in course_codes_to_course
        and course_codes_to_course[section.course_code] not in set(taken_courses)
        and not section_overlaps_timeslots(section, unavailability_times)
    ]
    
    def get_section_score(section: Section) -> float:
        score = course_scores[course_codes_to_course[section.course_code]]
        if section_overlaps_timeslots(section, avoid_times):
            score -= 10
        
        # Add average instructor rating to the score
        if instructor_ratings_map and section.instructor_names:
            instructor_ratings = []
            for name in section.instructor_names:
                name_stripped = name.strip()
                # Try exact match first, then case-insensitive match
                rating = (
                    instructor_ratings_map.get(name_stripped) or
                    instructor_ratings_map.get(name_stripped.lower())
                )
                if rating is not None:
                    instructor_ratings.append(rating)
            
            # Calculate average rating if we have any valid ratings
            if instructor_ratings:
                avg_rating = sum(instructor_ratings) / len(instructor_ratings)
                # Add the average rating to the score (ratings are typically 0-5)
                score += avg_rating
        
        return score

    sections_sorted = sorted(
        sections,
        key=get_section_score,
        reverse=True,
    )

    # Filter out sections where prerequisites are not satisfied
    sections_sorted = [
        section
        for section in sections_sorted
        if (
            course := course_codes_to_course[section.course_code]
        ).prerequisites is None
        or course.prerequisites.is_satisfied_by(taken_courses)
    ]

    return [
        SectionWithRequirementsFulfilled(
            section=section,
            fulfilled_requirements=course_to_requirements.get(
                course_codes_to_course[section.course_code], []
            )
        )
        for section in sections_sorted
    ]



def get_schedule(
    degree: Degree,
    student: Student,
    taken_courses: Sequence[CourseWithAttributes],
    all_courses: Sequence[CourseWithAttributes],
    all_sections: Sequence[Section],
    course_equivalencies: Sequence[Sequence[CourseCode]],
    unavailability_times: Sequence[TimeSlot] = [],
    avoid_times: Sequence[TimeSlot] = [],
    instructor_ratings_map: dict[str, float] | None = None,
) -> Sequence[SectionWithRequirementsFulfilled]:
    recommended_sections = get_recommended_sections(
        degree,
        student,
        taken_courses,
        all_courses,
        all_sections,
        course_equivalencies,
        unavailability_times,
        avoid_times,
        instructor_ratings_map,
    )
    
    # Calculate remaining needed for each requirement
    # Re-calculate including desired courses
    all_requirements = get_combined_requirements(degree, student, all_courses)
    
    requirements_status = {}
    for req in all_requirements:
        satisfied_count = 0
        for course in taken_courses:
            if req.course_rules.is_satisfied_by(course):
                satisfied_count += 1
        requirements_status[req.label] = max(0, req.needed - satisfied_count)

    schedule: Sequence[SectionWithRequirementsFulfilled] = []
    added_course_codes = set()
    
    # Dynamic greedy selection
    for _ in range(6):
        best_section_wrapper = None
        best_score = 0
        
        for rec in recommended_sections:
            section = rec.section
            
            # Skip if already added
            if section.course_code in added_course_codes:
                continue
            
            # Skip if overlaps with current schedule
            if any(section.overlaps(s.section) for s in schedule):
                continue

            # Calculate dynamic score: how many *currently needed* requirements does it satisfy?
            score = 0
            for req_label in rec.fulfilled_requirements:
                if requirements_status.get(req_label, 0) > 0:
                    score += 1
            
            # We want the section that satisfies the MOST needed requirements
            if score > best_score:
                best_score = score
                best_section_wrapper = rec
        
        # If we found a useful section, add it
        if best_section_wrapper and best_score > 0:
            schedule.append(best_section_wrapper)
            added_course_codes.add(best_section_wrapper.section.course_code)
            
            # Decrement needed counts
            for req_label in best_section_wrapper.fulfilled_requirements:
                if requirements_status.get(req_label, 0) > 0:
                    requirements_status[req_label] -= 1
        else:
            # No more useful sections found
            break
    
    return schedule
