from fastapi import APIRouter, HTTPException, status
from billiken_blueprint.dependencies import CurrentStudent, StudentRepo, CourseRepo
from billiken_blueprint.domain.student import Student

router = APIRouter(prefix="/student/desired_courses", tags=["student"])

@router.post("")
async def add_desired_course(
    course_id: int,
    student: CurrentStudent,
    student_repo: StudentRepo,
    course_repo: CourseRepo
):
    course = await course_repo.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    if course_id not in student.desired_course_ids:
        student.desired_course_ids.append(course_id)
        await student_repo.save(student)
    
    return student.desired_course_ids

@router.delete("/{course_id}")
async def remove_desired_course(
    course_id: int,
    student: CurrentStudent,
    student_repo: StudentRepo
):
    if course_id in student.desired_course_ids:
        student.desired_course_ids.remove(course_id)
        await student_repo.save(student)
        
    return student.desired_course_ids
