from billiken_blueprint.scheduling.course_prereq import (
    CoursePrereqNode,
    CoursePrerequisite,
    Operand,
)


def is_req_satisfied(
    prereq: CoursePrereqNode | Operand | None, completed_course_codes: set[str]
) -> bool:
    """Recursively checks if a prerequisite node is satisfied given a set of completed course codes.

    Args:
        prereq (CoursePrereqNode | Operand): The prerequisite node to check.
        completed_course_codes (set[str]): A set of course codes that have been completed.

    Returns:
        bool: True if the prerequisite is satisfied, False otherwise.
    """
    if prereq is None:
        return True

    if isinstance(prereq, CoursePrereqNode):
        if prereq.to:
            code_nums = [
                int(code.split()[-1])
                for code in completed_course_codes
                if code.startswith(prereq.course_code.split()[0])
            ]
            start_code_num = int(prereq.course_code.split()[-1])
            return any(
                code_num >= start_code_num and code_num <= prereq.to
                for code_num in code_nums
            )

        return prereq.course_code in completed_course_codes

    if prereq.operator == "AND":
        return all(
            is_req_satisfied(child, completed_course_codes) for child in prereq.operands
        )
    elif prereq.operator == "OR":
        return any(
            is_req_satisfied(child, completed_course_codes) for child in prereq.operands
        )

    return False


def are_prereqs_satisfied(
    course: CoursePrerequisite, completed_course_codes: set[str]
) -> bool:
    """Checks if the prerequisites for a course are satisfied given a set of completed course codes.

    Args:
        course (CoursePrerequisite): The course whose prerequisites are to be checked.
        completed_course_codes (set[str]): A set of course codes that have been completed.

    Returns:
        bool: True if all prerequisites are satisfied, False otherwise.
    """
    return is_req_satisfied(course.reqs, completed_course_codes)
