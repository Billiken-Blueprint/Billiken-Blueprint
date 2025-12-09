from dataclasses import asdict

from fastapi import APIRouter, Query
from pydantic import BaseModel

from billiken_blueprint.courses_at_slu.semester import Semester
from billiken_blueprint.dependencies import (
    CourseAttributeRepo,
    CourseRepo,
    CurrentStudent,
    DegreeRepo,
    InstructorRepo,
    RatingRepo,
    SectionRepo,
)
from billiken_blueprint.domain.courses.course import CourseWithAttributes
from billiken_blueprint.domain.courses.course_code import CourseCode
from billiken_blueprint.use_cases.get_schedule import (
    get_combined_requirements,
    get_schedule,
)


router = APIRouter(prefix="/degree-requirements", tags=["degree-requirements"])


@router.get("")
async def get_degree_requirements(
    student: CurrentStudent,
    degree_repo: DegreeRepo,
    course_repo: CourseRepo,
    course_attribute_repo: CourseAttributeRepo,
):
    all_courses = await course_repo.get_all()
    all_courses_with_attrs = [
        await CourseWithAttributes.from_course(course, course_attribute_repo)
        for course in all_courses
    ]
    degree = await degree_repo.get_by_id(student.degree_id)
    all_requirements = get_combined_requirements(
        degree, student, all_courses_with_attrs
    )
    return [
        dict(
            label=req.label,
            needed=req.needed,
            satisfyingCourseCodes=[
                f"{mc.major_code} {mc.course_number}"
                for mc in req.course_rules.filter_satisfying_courses(
                    all_courses_with_attrs
                )
            ],
            satisfyingCourseIds=[
                mc.id
                for mc in req.course_rules.filter_satisfying_courses(
                    all_courses_with_attrs
                )
            ],
        )
        for req in all_requirements
    ]


class AutogenerateScheduleMeetingTime(BaseModel):
    day: int
    startTime: str
    endTime: str


class AutogenerateScheduleSectionResponse(BaseModel):
    id: int | None
    crn: str
    instructorNames: list[str]
    campusCode: str
    description: str
    title: str
    courseCode: str
    semester: str
    meetingTimes: list[AutogenerateScheduleMeetingTime]
    requirementLabels: list[str]


class TimeSlotResponse(BaseModel):
    day: int
    start: str
    end: str


class AutogenerateScheduleResponse(BaseModel):
    sections: list[AutogenerateScheduleSectionResponse]
    unavailabilityTimes: list[TimeSlotResponse]
    avoidTimes: list[TimeSlotResponse]
    discardedSectionIds: list[int]


@router.get("/autogenerate-schedule", response_model=AutogenerateScheduleResponse)
async def autogenerate_schedule(
    student: CurrentStudent,
    course_repo: CourseRepo,
    degree_repo: DegreeRepo,
    sections_repo: SectionRepo,
    course_attribute_repo: CourseAttributeRepo,
    instructor_repo: InstructorRepo,
    rating_repo: RatingRepo,
    semester: str = Query(
        Semester.SPRING, description="Semester code (e.g., '202501' for Spring 2025)"
    ),
    discarded_section_ids: list[int] = Query(
        [], description="List of section IDs to exclude from the schedule"
    ),
):
    degree = await degree_repo.get_by_id(student.degree_id)
    all_courses = await course_repo.get_all()
    all_courses_with_attrs = [
        await CourseWithAttributes.from_course(course, course_attribute_repo)
        for course in all_courses
    ]
    taken_courses = [
        await course_repo.get_by_id(cid) for cid in student.completed_course_ids
    ]
    taken_courses_with_attrs = [
        await CourseWithAttributes.from_course(course, course_attribute_repo)
        for course in taken_courses
        if course
    ]
    all_sections = await sections_repo.get_all_for_semester(semester)
    all_sections = [
        section
        for section in all_sections
        if section.campus_code == "North Campus (Main Campus)"
    ]

    # Get all instructors and create a mapping of instructor name -> rating
    # Priority: RMP rating > aggregated user-submitted ratings
    all_instructors = await instructor_repo.get_all()
    instructor_ratings_map: dict[str, float] = {}

    # First, add RMP ratings (for CSCI and MATH departments)
    for instructor in all_instructors:
        if instructor.rmp_rating is not None:
            name_normalized = instructor.name.strip().lower()
            instructor_ratings_map[name_normalized] = instructor.rmp_rating
            instructor_ratings_map[instructor.name.strip()] = instructor.rmp_rating

    # Then, aggregate user-submitted ratings for instructors without RMP ratings
    # This covers all departments, not just CSCI and MATH
    all_user_ratings = await rating_repo.get_all()

    # Group ratings by instructor_id and calculate averages
    instructor_ratings_by_id: dict[int, list[int]] = {}
    for rating in all_user_ratings:
        if rating.professor_id and rating.rating_value is not None:
            if rating.professor_id not in instructor_ratings_by_id:
                instructor_ratings_by_id[rating.professor_id] = []
            instructor_ratings_by_id[rating.professor_id].append(rating.rating_value)

    # Calculate average ratings and add to map (only if RMP rating doesn't exist)
    for instructor in all_instructors:
        # Skip if already has RMP rating
        if instructor.rmp_rating is not None:
            continue

        # Check if instructor has user-submitted ratings
        if instructor.id and instructor.id in instructor_ratings_by_id:
            ratings = instructor_ratings_by_id[instructor.id]
            if ratings:
                avg_rating = sum(ratings) / len(ratings)
                # Only add if we have at least 2 ratings (to avoid single biased ratings)
                # Or if instructor doesn't have RMP rating and has user ratings
                if len(ratings) >= 1:  # Allow single ratings as fallback
                    name_normalized = instructor.name.strip().lower()
                    # Only add if not already in map (RMP takes priority)
                    if name_normalized not in instructor_ratings_map:
                        instructor_ratings_map[name_normalized] = avg_rating
                        instructor_ratings_map[instructor.name.strip()] = avg_rating

    schedule = get_schedule(
        degree,
        student,
        taken_courses_with_attrs,
        all_courses_with_attrs,
        all_sections,
        [
            [
                CourseCode("CORE", "1900"),
                CourseCode("ENGL", "1900"),
            ]
        ],
        unavailability_times=student.unavailability_times,
        avoid_times=student.avoid_times,
        instructor_ratings_map=instructor_ratings_map,
        discarded_section_ids=discarded_section_ids,
    )

    return AutogenerateScheduleResponse(
        sections=[
            AutogenerateScheduleSectionResponse(
                id=section.section.id,
                crn=section.section.crn,
                instructorNames=section.section.instructor_names,
                campusCode=section.section.campus_code,
                description=section.section.description,
                title=section.section.title,
                courseCode=section.section.course_code,
                semester=section.section.semester,
                meetingTimes=[
                    AutogenerateScheduleMeetingTime(
                        day=mt.day,
                        startTime=mt.start_time,
                        endTime=mt.end_time,
                    )
                    for mt in section.section.meeting_times
                ],
                requirementLabels=section.fulfilled_requirements,
            )
            for section in schedule
        ],
        unavailabilityTimes=[
            TimeSlotResponse(day=ts.day, start=ts.start, end=ts.end)
            for ts in student.unavailability_times
        ],
        avoidTimes=[
            TimeSlotResponse(day=ts.day, start=ts.start, end=ts.end)
            for ts in student.avoid_times
        ],
        discardedSectionIds=discarded_section_ids,
    )
