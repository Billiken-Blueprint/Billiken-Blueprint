from fastapi import APIRouter, Depends
from billiken_blueprint.scheduling.schedule_service import ScheduleService
from billiken_blueprint.repositories.student_repository import StudentRepository

router = APIRouter(prefix="/schedule", tags=["Scheduling"])


@router.get("/{student_id}")
async def get_schedule(student_id: int,
                       schedule_service: ScheduleService = Depends(),
                       student_repo: StudentRepository = Depends()):

    student = student_repo.get_student(student_id)
    recommended = await schedule_service.get_schedule_for_next_semester(student)

    return {
        "student_id": student_id,
        "recommended_courses": [
            {
                "major": c.major_code,
                "course_number": c.course_number,
                "attributes": [a.degree_works_label for a in c.attributes],
            }
            for c in recommended
        ]
    }
