from dataclasses import asdict

from fastapi import APIRouter, Query
from pydantic import BaseModel

from billiken_blueprint.courses_at_slu.semester import Semester
from billiken_blueprint.dependencies import (
    CourseAttributeRepo,
    CourseRepo,
    CurrentStudent,
    DegreeRepo,
    SectionRepo,
)
from billiken_blueprint.domain.courses.course import CourseWithAttributes
from billiken_blueprint.domain.courses.course_code import CourseCode


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
        )
        for req in degree.requirements
    ]


class AutogenerateScheduleMeetingTime(BaseModel):
    day: str
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

class AutogenerateScheduleResponse(BaseModel):
    sections: list[AutogenerateScheduleSectionResponse]

@router.get("/autogenerate-schedule", response_model=AutogenerateScheduleResponse)
async def autogenerate_schedule(
    student: CurrentStudent,
    course_repo: CourseRepo,
    degree_repo: DegreeRepo,
    sections_repo: SectionRepo,
    course_attribute_repo: CourseAttributeRepo,
    semester: str = Query(
        Semester.SPRING, description="Semester code (e.g., '202501' for Spring 2025)"
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
    all_sections = [section for section in all_sections if section.campus_code == "North Campus (Main Campus)"]
    
    schedule = degree.get_schedule(
        taken_courses_with_attrs,
        all_courses_with_attrs,
        all_sections,
        [
            [
                CourseCode("CORE", "1900"),
                CourseCode("ENGL", "1900"),
            ]
        ],
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
        ]
    )
