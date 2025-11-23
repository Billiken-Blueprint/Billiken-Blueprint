from billiken_blueprint.degree_works.course import (
    DegreeWorksCourse,
    DegreeWorksCourseGroup,
    DegreeWorksCourseRange,
)
from billiken_blueprint.domain.course import MinimalCourse
from billiken_blueprint.domain.degree import DegreeRequirement


def test_courses_satisfied():
    # Arrange
    courses = [
        DegreeWorksCourse("MATH", "1000"),
        DegreeWorksCourse("MATH", "2000"),
    ]
    course_group = DegreeWorksCourseGroup(courses=courses, exclude=[])

    # Act
    assert course_group.is_satisfied_by(MinimalCourse(None, "MATH", "1000", []))
    assert course_group.is_satisfied_by(MinimalCourse(None, "MATH", "2000", []))


def test_courses_not_satisfied():
    # Arrange
    courses = [
        DegreeWorksCourse("MATH", "1000"),
        DegreeWorksCourse("MATH", "2000"),
    ]
    course_group = DegreeWorksCourseGroup(courses=courses, exclude=[])

    # Act
    assert not course_group.is_satisfied_by(MinimalCourse(None, "MATH", "3000", []))
    assert not course_group.is_satisfied_by(MinimalCourse(None, "PHYS", "1000", []))


def test_course_range_satisfied():
    # Arrange
    courses = [
        DegreeWorksCourseRange("MATH", "1500", "2500"),
    ]
    course_group = DegreeWorksCourseGroup(courses=courses, exclude=[])

    # Act
    assert course_group.is_satisfied_by(MinimalCourse(None, "MATH", "1500", []))
    assert course_group.is_satisfied_by(MinimalCourse(None, "MATH", "2000", []))
    assert course_group.is_satisfied_by(MinimalCourse(None, "MATH", "2500", []))


def test_course_range_not_satisfied():
    # Arrange
    courses = [
        DegreeWorksCourseRange("MATH", "1500", "2500"),
    ]
    course_group = DegreeWorksCourseGroup(courses=courses, exclude=[])

    # Act
    assert not course_group.is_satisfied_by(MinimalCourse(None, "MATH", "1400", []))
    assert not course_group.is_satisfied_by(MinimalCourse(None, "MATH", "2600", []))
    assert not course_group.is_satisfied_by(MinimalCourse(None, "PHYS", "2600", []))


def test_excluded_course_not_satisfied():
    # Arrange
    courses = [
        DegreeWorksCourseRange("MATH", "2000", "3000"),
    ]
    exclude = [
        DegreeWorksCourse("MATH", "2050"),
    ]
    course_group = DegreeWorksCourseGroup(courses=courses, exclude=exclude)

    # Act
    assert not course_group.is_satisfied_by(MinimalCourse(None, "MATH", "2050", []))


def test_degree_requirement_with_multiple_required():
    # Arrange
    courses = [
        DegreeWorksCourse("MATH", "1000"),
        DegreeWorksCourseRange("PHYS", "2000", "3000"),
    ]
    exclude = [
        DegreeWorksCourse("PHYS", "2500"),
    ]
    course_group = DegreeWorksCourseGroup(courses=courses, exclude=exclude)
    req = DegreeRequirement("Test Requirement", needed=2, course_group=course_group)

    # Act & Assert
    assert req.is_satisfied_by(
        [
            MinimalCourse(None, "MATH", "1000", []),
            MinimalCourse(None, "PHYS", "2000", []),
        ]
    )
    assert req.is_satisfied_by(
        [
            MinimalCourse(None, "PHYS", "2000", []),
            MinimalCourse(None, "PHYS", "3000", []),
        ]
    )
    assert req.is_satisfied_by(
        [
            MinimalCourse(None, "MATH", "1000", []),
            MinimalCourse(None, "PHYS", "2000", []),
            MinimalCourse(None, "PHYS", "3000", []),
        ]
    )
    assert not req.is_satisfied_by(
        [
            MinimalCourse(None, "MATH", "1000", []),
            MinimalCourse(None, "PHYS", "2500", []),
        ]
    )
    assert not req.is_satisfied_by(
        [
            MinimalCourse(None, "MATH", "1000", []),
        ]
    )
    assert not req.is_satisfied_by([])
    assert not req.is_satisfied_by(
        [
            MinimalCourse(None, "CSCI", "2000", []),
            MinimalCourse(None, "CSCI", "2050", []),
            MinimalCourse(None, "CSCI", "3000", []),
        ]
    )
