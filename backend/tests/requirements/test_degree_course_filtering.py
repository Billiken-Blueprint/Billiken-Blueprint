import pytest
from billiken_blueprint.degree_works.course import (
    DegreeWorksCourse,
    DegreeWorksCourseGroup,
    DegreeWorksCourseRange,
)
from billiken_blueprint.domain.course import MinimalCourse
from billiken_blueprint.domain.degree import Degree, DegreeRequirement


@pytest.fixture()
def available_courses():
    return [
        MinimalCourse(
            id=None,
            major_code="CSCI",
            course_number="1000",
            attributes=[],
        ),
        MinimalCourse(
            id=None,
            major_code="CSCI",
            course_number="2000",
            attributes=[],
        ),
        MinimalCourse(id=None, major_code="CSCI", course_number="1500", attributes=[]),
        MinimalCourse(
            id=None,
            major_code="MATH",
            course_number="1500",
            attributes=[],
        ),
        MinimalCourse(
            id=None,
            major_code="MATH",
            course_number="1050",
            attributes=[],
        ),
        MinimalCourse(
            id=None,
            major_code="PHYS",
            course_number="1000",
            attributes=[],
        ),
    ]


@pytest.fixture()
def course_group1():
    courses_req = [
        DegreeWorksCourse(major_code="CSCI", course_number="1000"),
        DegreeWorksCourse(major_code="CSCI", course_number="2000"),
        DegreeWorksCourseRange("MATH", "1000", "2000"),
    ]
    exclude_courses = [
        DegreeWorksCourse(major_code="MATH", course_number="1050"),
    ]
    course_group = DegreeWorksCourseGroup(courses=courses_req, exclude=exclude_courses)
    return course_group


@pytest.fixture()
def course_group2():
    courses_req = [
        DegreeWorksCourse(major_code="CSCI", course_number="1500"),
        DegreeWorksCourse(major_code="CSCI", course_number="2500"),
        DegreeWorksCourseRange("MATH", "2000", "4000"),
    ]
    exclude_courses = [
        DegreeWorksCourse(major_code="MATH", course_number="1050"),
    ]
    course_group = DegreeWorksCourseGroup(courses=courses_req, exclude=exclude_courses)
    return course_group


def test_filter_courses_satisfying_course_group(course_group1, available_courses):
    # Arrange
    # Act
    satisfying_courses = course_group1.filter_satisfying_courses(available_courses)

    # Assert
    satisfying_courses_list = list(satisfying_courses)
    assert len(satisfying_courses_list) == 3
    assert any(
        course.major_code == "CSCI" and course.course_number == "1000"
        for course in satisfying_courses_list
    )
    assert any(
        course.major_code == "CSCI" and course.course_number == "2000"
        for course in satisfying_courses_list
    )
    assert any(
        course.major_code == "MATH" and course.course_number == "1500"
        for course in satisfying_courses_list
    )


def test_filter_courses_satisfying_degree(
    available_courses, course_group1, course_group2
):
    # Arrange
    courses_req = [
        DegreeWorksCourse(major_code="CSCI", course_number="1000"),
        DegreeWorksCourse(major_code="CSCI", course_number="2000"),
        DegreeWorksCourseRange("MATH", "1000", "2000"),
    ]
    exclude_courses = [
        DegreeWorksCourse(major_code="MATH", course_number="1050"),
    ]
    course_group = DegreeWorksCourseGroup(courses=courses_req, exclude=exclude_courses)
    degree = Degree(
        "",
        [
            DegreeRequirement("", 2, course_group1),
            DegreeRequirement("", 1, course_group2),
        ],
    )

    # Act
    satisfying_courses = degree.filter_courses_satisfying_unsatisfied_requirements(
        available_courses,
        [
            MinimalCourse(None, "CSCI", "1000", []),
            MinimalCourse(None, "CSCI", "2000", []),
        ],
    )

    # Assert
    satisfying_courses_list = list(satisfying_courses)
    assert len(satisfying_courses_list) == 1
    assert any(
        course.major_code == "CSCI" and course.course_number == "1500"
        for course in satisfying_courses_list
    )
