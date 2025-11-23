from dataclasses import dataclass
from typing import Sequence

from billiken_blueprint.degree_works.course import DegreeWorksCourseGroup
from billiken_blueprint.domain.course import MinimalCourse
from billiken_blueprint.domain.section import Section
from billiken_blueprint.domain.course_prereq import CoursePrereq


@dataclass
class SectionWithRequirement:
    """A section paired with the degree requirement it fulfills."""

    section: Section
    requirement_label: str


@dataclass(frozen=True)
class DegreeRequirement:
    label: str
    needed: int
    course_group: DegreeWorksCourseGroup

    def is_satisfied_by(self, courses: Sequence[MinimalCourse]) -> bool:
        satisfied_count = 0
        for course in courses:
            if self.course_group.is_satisfied_by(course):
                satisfied_count += 1
                if satisfied_count >= int(self.needed):
                    return True
        return False

    def filter_untaken_courses_satisfying_requirement(
        self, courses: Sequence[MinimalCourse], courses_taken: Sequence[MinimalCourse]
    ) -> list[MinimalCourse]:
        courses_taken_set = set(courses_taken)
        courses = [course for course in courses if course not in courses_taken_set]
        satisfying_courses = []
        for course in courses:
            if self.course_group.is_satisfied_by(course):
                satisfying_courses.append(course)
        return satisfying_courses


@dataclass
class Degree:
    name: str
    requirements: list[DegreeRequirement]

    def filter_courses_satisfying_unsatisfied_requirements(
        self,
        courses: Sequence[MinimalCourse],
        courses_taken: Sequence[MinimalCourse],
    ) -> Sequence[MinimalCourse]:
        reqs = [
            req for req in self.requirements if not req.is_satisfied_by(courses_taken)
        ]
        satisfying_courses = set(
            course
            for req in reqs
            for course in req.filter_untaken_courses_satisfying_requirement(
                courses, courses_taken
            )
        )
        return list(satisfying_courses)

    def autogenerate_schedule(
        self, sections: Sequence[Section], courses_taken: Sequence[MinimalCourse]
    ) -> Sequence[Section]:
        return []

    def suggest_sections_maximizing_requirements(
        self,
        all_sections: Sequence[Section],
        courses_taken: Sequence[MinimalCourse],
        course_prerequisites_map: dict[str, CoursePrereq | None],
        semester: str,
        limit: int = 6,
        major_balance: float = 0.5,
    ) -> list[SectionWithRequirement]:
        """
        Suggest sections that maximize the number of different degree requirements satisfied.
        This ensures diverse course suggestions across multiple requirements rather than
        all suggestions coming from a single requirement.

        IMPORTANT: Only suggests courses where ALL prerequisites have been met.
        IMPORTANT: Excludes courses that are prerequisites of already-taken courses.
        IMPORTANT: Excludes sections with no meeting times (e.g., online/async courses).
        IMPORTANT: Respects each requirement's "needed" count - won't suggest more courses
                   than required to satisfy each requirement.

        Strategy:
        1. Find all unsatisfied requirements
        2. Separate requirements into university core vs major requirements
        3. Use major_balance to determine proportion of each type to suggest
        4. For each requirement, find sections with satisfied prerequisites
        5. Filter out courses that are prerequisites of courses already taken
        6. Continue adding sections from different requirements until limit is reached
        7. Track count per requirement and stop when requirement.needed is reached
        8. If we've covered all requirements and still have room, add more sections

        Args:
            all_sections: All available sections
            courses_taken: Courses the student has already completed
            course_prerequisites_map: Map of course codes to their prerequisites
            semester: The semester to filter sections for
            limit: Maximum number of sections to return (default: 6)
            major_balance: Proportion of major requirements vs university core (0.0-1.0).
                          0.5 = 50% major, 50% core. 0.7 = 70% major, 30% core.
                          If core requirements are all satisfied, will use major only.

        Returns:
            List of SectionWithRequirement objects that maximize requirement coverage (prerequisites met)
        """
        from collections import defaultdict

        # Get all unsatisfied requirements
        unsatisfied_requirements = [
            req for req in self.requirements if not req.is_satisfied_by(courses_taken)
        ]

        if not unsatisfied_requirements:
            return []

        # Filter sections for the specified semester
        semester_sections = [s for s in all_sections if s.semester == semester]

        # Filter out sections with no meeting times (online/async courses without scheduled times)
        semester_sections = [s for s in semester_sections if len(s.meeting_times) > 0]

        # Group sections by course code
        sections_by_course: dict[str, list[Section]] = defaultdict(list)
        for section in semester_sections:
            sections_by_course[section.course_code].append(section)

        # Build a set of course codes to exclude (already taken or prerequisites of taken courses)
        courses_taken_codes = {
            f"{c.major_code} {c.course_number}" for c in courses_taken
        }

        # Build set of all prerequisite courses from taken courses (optimization)
        excluded_course_codes = courses_taken_codes.copy()
        for taken_course in courses_taken:
            taken_course_code = (
                f"{taken_course.major_code} {taken_course.course_number}"
            )
            prereqs = course_prerequisites_map.get(taken_course_code)
            if prereqs is not None:
                excluded_course_codes.update(
                    self._extract_prerequisite_course_codes(prereqs)
                )

        # Build a list of (requirement, scored sections) tuples
        requirement_sections: list[
            tuple[DegreeRequirement, list[tuple[Section, int]]]
        ] = []

        for requirement in unsatisfied_requirements:
            scored_sections = []

            for course_code, sections in sections_by_course.items():
                # Skip if already taken or is a prerequisite of a taken course
                if course_code in excluded_course_codes:
                    continue

                # Check if this course satisfies the requirement
                major_code, course_number = course_code.split()
                temp_course = MinimalCourse(
                    id=None,
                    major_code=major_code,
                    course_number=course_number,
                    attributes=[],
                )

                if self._course_satisfies_requirement(temp_course, requirement):
                    # Only include sections if prerequisites are met
                    prereqs = course_prerequisites_map.get(course_code)
                    # Include if no prerequisites exist OR prerequisites are satisfied
                    if prereqs is None or prereqs.is_satisfied_by(courses_taken):
                        # Score all sections of this course
                        for section in sections:
                            score = self._calculate_prerequisite_score(
                                section, courses_taken, course_prerequisites_map
                            )
                            scored_sections.append((section, score))

            # Sort by score (descending), then by CRN
            scored_sections.sort(key=lambda x: (-x[1], x[0].crn))
            requirement_sections.append((requirement, scored_sections))

        # Separate requirements into university core and major requirements
        core_requirements = [
            (req, sections)
            for req, sections in requirement_sections
            if self._is_university_core_requirement(req)
        ]
        major_requirements = [
            (req, sections)
            for req, sections in requirement_sections
            if not self._is_university_core_requirement(req)
        ]

        # Calculate how many of each type to suggest based on major_balance
        # If all core requirements are satisfied, use major only
        if not core_requirements:
            target_major_count = limit
            target_core_count = 0
        else:
            target_major_count = int(limit * major_balance)
            target_core_count = limit - target_major_count

        # Now select sections to maximize requirement coverage
        result_sections: list[SectionWithRequirement] = []
        selected_course_codes: set[str] = set()

        # Track how many courses have been suggested per requirement
        requirement_counts: dict[str, int] = {}
        for requirement, _ in requirement_sections:
            requirement_counts[requirement.label] = 0

        # Build a mapping from section course_code to requirement (for tracking in phase 2)
        section_to_requirement: dict[str, DegreeRequirement] = {}
        for requirement, sections in requirement_sections:
            for section, score in sections:
                if section.course_code not in section_to_requirement:
                    section_to_requirement[section.course_code] = requirement

        # Track how many of each type we've added
        core_count = 0
        major_count = 0

        # Phase 1: Add sections based on major_balance ratio
        # First, try to get one section per requirement, respecting the balance

        # Alternate between core and major requirements based on the ratio
        core_index = 0
        major_index = 0

        while len(result_sections) < limit and (
            core_index < len(core_requirements) or major_index < len(major_requirements)
        ):
            # Determine if we should add a core or major requirement next
            # based on how close we are to our targets
            should_add_core = False
            should_add_major = False

            if core_index < len(core_requirements) and core_count < target_core_count:
                should_add_core = True
            if (
                major_index < len(major_requirements)
                and major_count < target_major_count
            ):
                should_add_major = True

            # If we can add both, prioritize based on which is further from its target proportion
            if should_add_core and should_add_major:
                core_proportion = core_count / max(target_core_count, 1)
                major_proportion = major_count / max(target_major_count, 1)
                should_add_core = core_proportion <= major_proportion
                should_add_major = not should_add_core

            # Try to add a core requirement
            if should_add_core and core_index < len(core_requirements):
                requirement, sections = core_requirements[core_index]
                core_index += 1

                # Check if we've already suggested enough courses for this requirement
                if requirement_counts[requirement.label] >= int(requirement.needed):
                    continue

                # Find the best section we haven't already selected
                for section, score in sections:
                    if section.course_code not in selected_course_codes:
                        # Check for time conflicts with already selected sections
                        if not self._schedule_has_conflict_with_section(
                            [s.section for s in result_sections], section
                        ):
                            result_sections.append(
                                SectionWithRequirement(
                                    section=section, requirement_label=requirement.label
                                )
                            )
                            selected_course_codes.add(section.course_code)
                            requirement_counts[requirement.label] += 1
                            core_count += 1
                            break

            # Try to add a major requirement
            elif should_add_major and major_index < len(major_requirements):
                requirement, sections = major_requirements[major_index]
                major_index += 1

                # Check if we've already suggested enough courses for this requirement
                if requirement_counts[requirement.label] >= int(requirement.needed):
                    continue

                # Find the best section we haven't already selected
                for section, score in sections:
                    if section.course_code not in selected_course_codes:
                        # Check for time conflicts with already selected sections
                        if not self._schedule_has_conflict_with_section(
                            [s.section for s in result_sections], section
                        ):
                            result_sections.append(
                                SectionWithRequirement(
                                    section=section, requirement_label=requirement.label
                                )
                            )
                            selected_course_codes.add(section.course_code)
                            requirement_counts[requirement.label] += 1
                            major_count += 1
                            break
            else:
                # Can't add anything, exit
                break

        # Phase 2: If we still have room, add more high-priority sections
        # respecting the balance and requirement needs
        if len(result_sections) < limit:
            # Collect all remaining sections, sorted by score
            core_scored_sections = []
            major_scored_sections = []

            for requirement, sections in core_requirements:
                # Only include sections if requirement still needs more courses
                if requirement_counts[requirement.label] < int(requirement.needed):
                    for section, score in sections:
                        if section.course_code not in selected_course_codes:
                            core_scored_sections.append((section, score, requirement))

            for requirement, sections in major_requirements:
                # Only include sections if requirement still needs more courses
                if requirement_counts[requirement.label] < int(requirement.needed):
                    for section, score in sections:
                        if section.course_code not in selected_course_codes:
                            major_scored_sections.append((section, score, requirement))

            # Sort both lists by score (descending), then by CRN
            core_scored_sections.sort(key=lambda x: (-x[1], x[0].crn))
            major_scored_sections.sort(key=lambda x: (-x[1], x[0].crn))

            core_phase2_index = 0
            major_phase2_index = 0

            # Add until we reach the limit, respecting balance
            while len(result_sections) < limit and (
                core_phase2_index < len(core_scored_sections)
                or major_phase2_index < len(major_scored_sections)
            ):
                # Determine if we should add core or major based on targets
                should_add_core = False
                should_add_major = False

                if (
                    core_phase2_index < len(core_scored_sections)
                    and core_count < target_core_count
                ):
                    should_add_core = True
                if (
                    major_phase2_index < len(major_scored_sections)
                    and major_count < target_major_count
                ):
                    should_add_major = True

                # If we've met our targets, fill remaining slots with whatever is available
                if not should_add_core and not should_add_major:
                    if core_phase2_index < len(core_scored_sections):
                        should_add_core = True
                    elif major_phase2_index < len(major_scored_sections):
                        should_add_major = True

                # If we can add both, prioritize based on score or proportion
                if should_add_core and should_add_major:
                    # Pick the one with higher score
                    core_score = (
                        core_scored_sections[core_phase2_index][1]
                        if core_phase2_index < len(core_scored_sections)
                        else -1
                    )
                    major_score = (
                        major_scored_sections[major_phase2_index][1]
                        if major_phase2_index < len(major_scored_sections)
                        else -1
                    )

                    if core_score >= major_score:
                        should_add_major = False
                    else:
                        should_add_core = False

                if should_add_core and core_phase2_index < len(core_scored_sections):
                    section, score, requirement = core_scored_sections[
                        core_phase2_index
                    ]
                    core_phase2_index += 1

                    # Check if this requirement already has enough suggestions
                    if requirement_counts[requirement.label] >= int(requirement.needed):
                        continue

                    if section.course_code not in selected_course_codes:
                        # Check for time conflicts
                        if not self._schedule_has_conflict_with_section(
                            [s.section for s in result_sections], section
                        ):
                            result_sections.append(
                                SectionWithRequirement(
                                    section=section, requirement_label=requirement.label
                                )
                            )
                            selected_course_codes.add(section.course_code)
                            requirement_counts[requirement.label] += 1
                            core_count += 1

                elif should_add_major and major_phase2_index < len(
                    major_scored_sections
                ):
                    section, score, requirement = major_scored_sections[
                        major_phase2_index
                    ]
                    major_phase2_index += 1

                    # Check if this requirement already has enough suggestions
                    if requirement_counts[requirement.label] >= int(requirement.needed):
                        continue

                    if section.course_code not in selected_course_codes:
                        # Check for time conflicts
                        if not self._schedule_has_conflict_with_section(
                            [s.section for s in result_sections], section
                        ):
                            result_sections.append(
                                SectionWithRequirement(
                                    section=section, requirement_label=requirement.label
                                )
                            )
                            selected_course_codes.add(section.course_code)
                            requirement_counts[requirement.label] += 1
                            major_count += 1
                else:
                    break

        return result_sections

    def suggest_sections_for_unsatisfied_requirement(
        self,
        requirement: DegreeRequirement,
        all_sections: Sequence[Section],
        courses_taken: Sequence[MinimalCourse],
        course_prerequisites_map: dict[str, CoursePrereq | None],
        semester: str,
        limit: int = 6,
    ) -> list[Section]:
        """
        Suggest 5-6 sections that satisfy an unsatisfied degree requirement.

        IMPORTANT: Only suggests courses where ALL prerequisites have been met.
        IMPORTANT: Excludes courses that are prerequisites of already-taken courses.
        IMPORTANT: Excludes sections with no meeting times (e.g., online/async courses).

        Args:
            requirement: The degree requirement to satisfy
            all_sections: All available sections
            courses_taken: Courses the student has already completed
            course_prerequisites_map: Map of course codes to their prerequisites
            semester: The semester to filter sections for
            limit: Maximum number of sections to return (default: 6)

        Returns:
            List of Section objects where prerequisites are satisfied
        """
        from collections import defaultdict

        # Filter sections for the specified semester
        semester_sections = [s for s in all_sections if s.semester == semester]

        # Filter out sections with no meeting times (online/async courses without scheduled times)
        semester_sections = [s for s in semester_sections if len(s.meeting_times) > 0]

        # Group sections by course code
        sections_by_course: dict[str, list[Section]] = defaultdict(list)
        for section in semester_sections:
            sections_by_course[section.course_code].append(section)

        # Build a set of course codes to exclude (already taken or prerequisites of taken courses)
        courses_taken_codes = {
            f"{c.major_code} {c.course_number}" for c in courses_taken
        }

        # Build set of all prerequisite courses from taken courses (optimization)
        excluded_course_codes = courses_taken_codes.copy()
        for taken_course in courses_taken:
            taken_course_code = (
                f"{taken_course.major_code} {taken_course.course_number}"
            )
            prereqs = course_prerequisites_map.get(taken_course_code)
            if prereqs is not None:
                excluded_course_codes.update(
                    self._extract_prerequisite_course_codes(prereqs)
                )

        satisfying_sections: list[Section] = []
        for course_code, sections in sections_by_course.items():
            # Skip if already taken or is a prerequisite of a taken course
            if course_code in excluded_course_codes:
                continue

            # Check if any section of this course satisfies the requirement
            # We need to create a MinimalCourse to check against the requirement
            major_code, course_number = course_code.split()
            temp_course = MinimalCourse(
                id=None,
                major_code=major_code,
                course_number=course_number,
                attributes=[],
            )

            if self._course_satisfies_requirement(temp_course, requirement):
                # Only include sections if prerequisites are met
                prereqs = course_prerequisites_map.get(course_code)
                # Include if no prerequisites exist OR prerequisites are satisfied
                if prereqs is None or prereqs.is_satisfied_by(courses_taken):
                    # Add all sections of this course
                    satisfying_sections.extend(sections)

        # Score each section based on prerequisite satisfaction
        scored_sections: list[tuple[Section, int]] = []
        for section in satisfying_sections:
            score = self._calculate_prerequisite_score(
                section, courses_taken, course_prerequisites_map
            )
            scored_sections.append((section, score))

        # Sort by score (higher is better - prerequisites met)
        # Then by CRN for consistency
        scored_sections.sort(key=lambda x: (-x[1], x[0].crn))

        # Return top N sections
        return [section for section, _ in scored_sections[:limit]]

    def _course_satisfies_requirement(
        self, course: MinimalCourse, requirement: DegreeRequirement
    ) -> bool:
        """Check if a course satisfies a degree requirement."""
        return requirement.course_group.is_satisfied_by(course)

    def _is_university_core_requirement(self, requirement: DegreeRequirement) -> bool:
        """
        Check if a requirement is a university core requirement.

        University core requirements are identified by checking if they require courses
        with specific university core attributes (UIS, UUQP, UUQT, UCI, USCM, USCN, USW,
        UAHC, UNAS, UQR, USBD, UWVC, UOVC, UCE, UWI, UIIC, UGI, UDEJ, URIA).

        Args:
            requirement: The degree requirement to check

        Returns:
            True if this is a university core requirement, False otherwise
        """
        from billiken_blueprint.degree_works.course import (
            DegreeWorksAnyCourseWithAttribute,
        )

        # Define the set of university core attribute codes
        UNIVERSITY_CORE_ATTRIBUTES = {
            "UIS",
            "UUQP",
            "UUQT",
            "UCI",
            "USCM",
            "USCN",
            "USW",
            "UAHC",
            "UNAS",
            "UQR",
            "USBD",
            "UWVC",
            "UOVC",
            "UCE",
            "UWI",
            "UIIC",
            "UGI",
            "UDEJ",
            "URIA",
        }

        for course in requirement.course_group.courses:
            if isinstance(course, DegreeWorksAnyCourseWithAttribute):
                # Check if any of the attributes in this course group are university core attributes
                for attr in course.attributes:
                    if attr in UNIVERSITY_CORE_ATTRIBUTES:
                        return True
        return False

    def _calculate_prerequisite_score(
        self,
        section: Section,
        courses_taken: Sequence[MinimalCourse],
        course_prerequisites_map: dict[str, CoursePrereq | None],
    ) -> int:
        """
        Calculate a score based on how well prerequisites are met.

        Returns:
            2 - Prerequisites fully met or no prerequisites
            1 - Some prerequisites met
            0 - No prerequisites met
        """
        prereqs = course_prerequisites_map.get(section.course_code)

        # No prerequisites or not found - give it a good score
        if prereqs is None:
            return 2

        # Check if prerequisites are satisfied
        if prereqs.is_satisfied_by(courses_taken):
            return 2

        # Partial credit - check if any prerequisite is met (for OR conditions)
        if self._has_partial_prerequisite_match(prereqs, courses_taken):
            return 1

        return 0

    def _has_partial_prerequisite_match(
        self, prereqs: CoursePrereq, courses_taken: Sequence[MinimalCourse]
    ) -> bool:
        """Check if any part of the prerequisite tree is satisfied."""
        from billiken_blueprint.domain.course_prereq import CoursePrereqCourse

        if prereqs.operator == "OR":
            # For OR, check if any operand is satisfied
            for operand in prereqs.operands:
                if isinstance(operand, CoursePrereqCourse):
                    if any(
                        course.major_code == operand.major_code
                        and operand.course_number <= int(course.course_number)
                        and (
                            operand.end_number is None
                            or int(course.course_number) <= operand.end_number
                        )
                        for course in courses_taken
                    ):
                        return True
                else:
                    if operand.is_satisfied_by(courses_taken):
                        return True
        elif prereqs.operator == "AND":
            # For AND, check if any operand is satisfied (partial match)
            for operand in prereqs.operands:
                if isinstance(operand, CoursePrereqCourse):
                    if any(
                        course.major_code == operand.major_code
                        and operand.course_number <= int(course.course_number)
                        and (
                            operand.end_number is None
                            or int(course.course_number) <= operand.end_number
                        )
                        for course in courses_taken
                    ):
                        return True
                else:
                    if operand.is_satisfied_by(courses_taken):
                        return True

        return False

    def _extract_prerequisite_course_codes(self, prereqs: CoursePrereq) -> set[str]:
        """
        Extract all course codes from a prerequisite tree.

        Args:
            prereqs: The prerequisite tree to extract courses from

        Returns:
            Set of course codes (e.g., "CSCI 1050") that appear in the prerequisite tree
        """
        from billiken_blueprint.domain.course_prereq import CoursePrereqCourse

        course_codes = set()

        for operand in prereqs.operands:
            if isinstance(operand, CoursePrereqCourse):
                # Handle single course or course range
                if (
                    operand.end_number is None
                    or operand.end_number == operand.course_number
                ):
                    # Single course
                    course_codes.add(f"{operand.major_code} {operand.course_number}")
                else:
                    # Course range - add all courses in the range
                    for course_num in range(
                        operand.course_number, operand.end_number + 1
                    ):
                        course_codes.add(f"{operand.major_code} {course_num}")
            else:
                # Nested requirement - recursively extract
                course_codes.update(self._extract_prerequisite_course_codes(operand))

        return course_codes

    def _times_overlap(
        self, time1_start: str, time1_end: str, time2_start: str, time2_end: str
    ) -> bool:
        """
        Check if two time ranges overlap.

        Args:
            time1_start: Start time in format "HH:MM" or "HHMM"
            time1_end: End time in format "HH:MM" or "HHMM"
            time2_start: Start time in format "HH:MM" or "HHMM"
            time2_end: End time in format "HH:MM" or "HHMM"

        Returns:
            True if the time ranges overlap, False otherwise
        """

        def parse_time(time_str: str) -> int:
            """Convert time string to minutes since midnight for comparison."""
            # Handle different formats: "HH:MM", "HHMM", or already an int
            if isinstance(time_str, int):
                time_str = str(time_str).zfill(4)

            time_str = time_str.strip()

            # Remove colon if present
            if ":" in time_str:
                time_str = time_str.replace(":", "")

            # Pad to 4 digits if needed
            time_str = time_str.zfill(4)

            hours = int(time_str[:2])
            minutes = int(time_str[2:4])

            return hours * 60 + minutes

        try:
            start1 = parse_time(time1_start)
            end1 = parse_time(time1_end)
            start2 = parse_time(time2_start)
            end2 = parse_time(time2_end)

            # Two time ranges overlap if one starts before the other ends
            # and vice versa
            return start1 < end2 and start2 < end1
        except (ValueError, IndexError):
            # If we can't parse the times, assume no overlap (conservative)
            return False

    def _sections_have_time_conflict(
        self, section1: Section, section2: Section
    ) -> bool:
        """
        Check if two sections have conflicting meeting times.

        Args:
            section1: First section
            section2: Second section

        Returns:
            True if sections have a time conflict, False otherwise
        """
        # Check each meeting time in section1 against each in section2
        for mt1 in section1.meeting_times:
            for mt2 in section2.meeting_times:
                # If they meet on the same day
                if mt1.day == mt2.day:
                    # Check if the times overlap
                    if self._times_overlap(
                        mt1.start_time, mt1.end_time, mt2.start_time, mt2.end_time
                    ):
                        return True

        return False

    def _schedule_has_conflict_with_section(
        self, existing_sections: list[Section], new_section: Section
    ) -> bool:
        """
        Check if adding a new section would create a time conflict with existing sections.

        Args:
            existing_sections: List of sections already in the schedule
            new_section: Section to potentially add

        Returns:
            True if there would be a conflict, False otherwise
        """
        for existing_section in existing_sections:
            if self._sections_have_time_conflict(existing_section, new_section):
                return True
        return False
