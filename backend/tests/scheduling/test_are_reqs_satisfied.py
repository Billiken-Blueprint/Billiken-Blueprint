from billiken_blueprint.scheduling.are_prereqs_satisfied import is_req_satisfied
from billiken_blueprint.scheduling.course_prereq import (
    CoursePrereqNode,
    Operand,
    CoursePrerequisite,
)


def test_one_req_satisfied():
    # Arrange
    req = CoursePrerequisite(
        course_code="CSCI 1070", reqs=CoursePrereqNode(course_code="CSCI 1060")
    )

    # Assert
    assert is_req_satisfied(req.reqs, {"CSCI 1060"})


def test_one_req_not_satisfied():
    # Arrange
    req = CoursePrerequisite(
        course_code="CSCI 1070", reqs=CoursePrereqNode(course_code="CSCI 1060")
    )

    # Assert
    assert not is_req_satisfied(req.reqs, {"CSCI 1050"})


def test_one_req_range_satisfied():
    # Arrange
    req = CoursePrerequisite(
        course_code="CSCI 3000",
        reqs=CoursePrereqNode(course_code="CSCI 2000", to=2099),
    )

    # Assert
    assert is_req_satisfied(req.reqs, {"CSCI 2050"})


def test_one_req_range_not_satisfied():
    # Arrange
    req = CoursePrerequisite(
        course_code="CSCI 3000",
        reqs=CoursePrereqNode(course_code="CSCI 2000", to=2099),
    )

    # Assert
    assert not is_req_satisfied(req.reqs, {"CSCI 2100"})


def test_and_reqs_satisfied():
    # Arrange
    req = CoursePrerequisite(
        course_code="CSCI 4000",
        reqs=Operand(
            operator="AND",
            operands=[
                CoursePrereqNode(course_code="CSCI 3000"),
                CoursePrereqNode(course_code="CSCI 3100"),
            ],
        ),
    )

    # Assert
    assert is_req_satisfied(req.reqs, {"CSCI 3000", "CSCI 3100"})


def test_and_reqs_not_satisfied():
    # Arrange
    req = CoursePrerequisite(
        course_code="CSCI 4000",
        reqs=Operand(
            operator="AND",
            operands=[
                CoursePrereqNode(course_code="CSCI 3000"),
                CoursePrereqNode(course_code="CSCI 3100"),
            ],
        ),
    )

    # Assert
    assert not is_req_satisfied(req.reqs, {"CSCI 3000"})


def test_or_reqs_satisfied():
    # Arrange
    req = CoursePrerequisite(
        course_code="CSCI 4000",
        reqs=Operand(
            operator="OR",
            operands=[
                CoursePrereqNode(course_code="CSCI 3000"),
                CoursePrereqNode(course_code="CSCI 3100"),
            ],
        ),
    )

    # Assert
    assert is_req_satisfied(req.reqs, {"CSCI 3100"})


def test_or_reqs_not_satisfied():
    # Arrange
    req = CoursePrerequisite(
        course_code="CSCI 4000",
        reqs=Operand(
            operator="OR",
            operands=[
                CoursePrereqNode(course_code="CSCI 3000"),
                CoursePrereqNode(course_code="CSCI 3100"),
            ],
        ),
    )

    # Assert
    assert not is_req_satisfied(req.reqs, {"CSCI 3200"})


def test_nested_reqs_satisfied():
    # Arrange
    req = CoursePrerequisite(
        course_code="CSCI 5000",
        reqs=Operand(
            operator="AND",
            operands=[
                CoursePrereqNode(course_code="CSCI 4000"),
                Operand(
                    operator="OR",
                    operands=[
                        CoursePrereqNode(course_code="CSCI 4100"),
                        CoursePrereqNode(course_code="CSCI 4200"),
                    ],
                ),
            ],
        ),
    )

    # Assert
    assert is_req_satisfied(req.reqs, {"CSCI 4000", "CSCI 4200"})


def test_nested_reqs_not_satisfied():
    # Arrange
    req = CoursePrerequisite(
        course_code="CSCI 5000",
        reqs=Operand(
            operator="AND",
            operands=[
                CoursePrereqNode(course_code="CSCI 4000"),
                Operand(
                    operator="OR",
                    operands=[
                        CoursePrereqNode(course_code="CSCI 4100"),
                        CoursePrereqNode(course_code="CSCI 4200"),
                    ],
                ),
            ],
        ),
    )

    # Assert
    assert not is_req_satisfied(req.reqs, {"CSCI 4000", "CSCI 4300"})


def test_no_reqs():
    # Arrange
    req = CoursePrerequisite(
        course_code="CSCI 1000",
        reqs=None,
    )

    # Assert
    assert is_req_satisfied(req.reqs, set())


def test_nested_range_reqs_satisfied():
    # Arrange
    req = CoursePrerequisite(
        course_code="CSCI 6000",
        reqs=Operand(
            operator="OR",
            operands=[
                Operand(
                    operator="AND",
                    operands=[
                        CoursePrereqNode(course_code="CSCI 4000", to=4999),
                        CoursePrereqNode(course_code="CSCI 5100"),
                    ],
                ),
                CoursePrereqNode(course_code="CSCI 5200", to=5299),
            ],
        ),
    )

    # Assert
    assert is_req_satisfied(req.reqs, {"CSCI 4050", "CSCI 5100"})


def test_nested_range_reqs_not_satisfied():
    # Arrange
    req = CoursePrerequisite(
        course_code="CSCI 6000",
        reqs=Operand(
            operator="OR",
            operands=[
                Operand(
                    operator="AND",
                    operands=[
                        CoursePrereqNode(course_code="CSCI 4000", to=4999),
                        CoursePrereqNode(course_code="CSCI 5100"),
                    ],
                ),
                CoursePrereqNode(course_code="CSCI 5200", to=5299),
            ],
        ),
    )

    # Assert
    assert not is_req_satisfied(req.reqs, {"CSCI 5050", "CSCI 5100"})
