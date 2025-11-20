import yaml
from billiken_blueprint.scheduling.course_prereq import (
    CoursePrereqNode,
    Operand,
)
from billiken_blueprint.scheduling.parse_course_reqs import parse_reqs


def test_parsing_one_req():
    # Arrange
    yaml_input = """
    courses:
      - code: CSCI 1070
        reqs:
          code: MATH 1200
    """

    # Act
    parsed_reqs = parse_reqs(yaml_input)

    # Assert
    assert len(parsed_reqs) == 1
    course_req = parsed_reqs[0]
    assert course_req.course_code == "CSCI 1070"
    assert isinstance(course_req.reqs, CoursePrereqNode)
    assert course_req.reqs.course_code == "MATH 1200"


def test_parsing_and_req():
    # Arrange
    yaml_input = """
    courses:
      - code: CSCI 1070
        reqs:
          operator: AND
          operands:
            - code: MATH 1200
            - code: CSCI 1010
    """

    # Act
    parsed_reqs = parse_reqs(yaml_input)

    # Assert
    assert len(parsed_reqs) == 1
    course_req = parsed_reqs[0]
    assert isinstance(course_req.reqs, Operand)
    assert course_req.course_code == "CSCI 1070"
    assert course_req.reqs.operator == "AND"
    assert len(course_req.reqs.operands) == 2
    assert isinstance(course_req.reqs.operands[0], CoursePrereqNode)
    assert course_req.reqs.operands[0].course_code == "MATH 1200"
    assert isinstance(course_req.reqs.operands[1], CoursePrereqNode)
    assert course_req.reqs.operands[1].course_code == "CSCI 1010"


def test_parsing_one_and_or_req():
    # Arrange
    yaml_input = """
    courses:
      - code: CSCI 1070
        reqs:
          operator: OR
          operands:
            - operator: AND
              operands:
                - code: MATH 1200
                - code: CSCI 1010
            - code: CSCI 1020
    """

    # Act
    parsed_reqs = parse_reqs(yaml_input)

    # Assert
    assert len(parsed_reqs) == 1
    course_req = parsed_reqs[0]
    assert isinstance(course_req.reqs, Operand)
    assert course_req.course_code == "CSCI 1070"
    assert course_req.reqs.operator == "OR"
    assert len(course_req.reqs.operands) == 2

    and_operand = course_req.reqs.operands[0]
    assert isinstance(and_operand, Operand)
    assert and_operand.operator == "AND"
    assert len(and_operand.operands) == 2
    assert isinstance(and_operand.operands[0], CoursePrereqNode)
    assert and_operand.operands[0].course_code == "MATH 1200"
    assert isinstance(and_operand.operands[1], CoursePrereqNode)
    assert and_operand.operands[1].course_code == "CSCI 1010"

    or_operand = course_req.reqs.operands[1]
    assert isinstance(or_operand, CoursePrereqNode)
    assert or_operand.course_code == "CSCI 1020"


def test_parsing_complex_req():
    # Arrange
    yaml_input = """
    courses:
      - code: CSCI 3000
        reqs:
          operator: AND
          operands:
            - operator: OR
              operands:
                - code: CSCI 2000
                - code: CSCI 2100
            - operator: AND
              operands:
                - code: MATH 2000
                - code: PHYS 1000
    """

    # Act
    parsed_reqs = parse_reqs(yaml_input)

    # Assert
    assert len(parsed_reqs) == 1
    course_req = parsed_reqs[0]
    assert isinstance(course_req.reqs, Operand)
    assert course_req.course_code == "CSCI 3000"
    assert course_req.reqs.operator == "AND"
    assert len(course_req.reqs.operands) == 2

    or_operand = course_req.reqs.operands[0]
    assert isinstance(or_operand, Operand)
    assert or_operand.operator == "OR"
    assert len(or_operand.operands) == 2
    assert isinstance(or_operand.operands[0], CoursePrereqNode)
    assert or_operand.operands[0].course_code == "CSCI 2000"
    assert isinstance(or_operand.operands[1], CoursePrereqNode)
    assert or_operand.operands[1].course_code == "CSCI 2100"

    and_operand = course_req.reqs.operands[1]
    assert isinstance(and_operand, Operand)
    assert and_operand.operator == "AND"
    assert len(and_operand.operands) == 2
    assert isinstance(and_operand.operands[0], CoursePrereqNode)
    assert and_operand.operands[0].course_code == "MATH 2000"
    assert isinstance(and_operand.operands[1], CoursePrereqNode)
    assert and_operand.operands[1].course_code == "PHYS 1000"


def test_parsing_multiple_courses():
    # Arrange
    yaml_input = """
    courses:
      - code: CSCI 1070
        reqs:
          code: MATH 1200
      - code: CSCI 2080
        reqs:
          operator: AND
          operands:
            - code: CSCI 1070
            - code: MATH 2200
    """

    # Act
    parsed_reqs = parse_reqs(yaml_input)

    # Assert
    assert len(parsed_reqs) == 2

    course_req1 = parsed_reqs[0]
    assert course_req1.course_code == "CSCI 1070"
    assert isinstance(course_req1.reqs, CoursePrereqNode)
    assert course_req1.reqs.course_code == "MATH 1200"

    course_req2 = parsed_reqs[1]
    assert course_req2.course_code == "CSCI 2080"
    assert isinstance(course_req2.reqs, Operand)
    assert course_req2.reqs.operator == "AND"
    assert len(course_req2.reqs.operands) == 2
    assert isinstance(course_req2.reqs.operands[0], CoursePrereqNode)
    assert course_req2.reqs.operands[0].course_code == "CSCI 1070"
    assert isinstance(course_req2.reqs.operands[1], CoursePrereqNode)
    assert course_req2.reqs.operands[1].course_code == "MATH 2200"
