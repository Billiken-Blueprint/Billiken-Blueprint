from billiken_blueprint.domain.degree import Degree
from billiken_blueprint.domain.course import MinimalCourse
from billiken_blueprint.domain.student import Student

class ScheduleService:
    def __init__(self, degree_repo, course_repo, prereq_service):
        self.degree_repo = degree_repo
        self.course_repo = course_repo
        self.prereq_service = prereq_service

    async def get_schedule_for_next_semester(self, student: Student) -> list[MinimalCourse]:
        # gets student data
        completed_courses = self.course_repo.get_minimal_by_ids(student.completed_course_ids)

        # gets degrees
        degrees: list[Degree] = [
            self.degree_repo.get_degree(degree_id)
            for degree_id in student.degree_ids
        ]

        # gets all courses offered 
        offered_courses: list[MinimalCourse] = self.course_repo.get_all_minimal_offered_next_sem()

        # combine degree recommendations
        recommended = set()
        for degree in degrees:
            degree_recs = degree.filter_courses_satisfying_unsatisfied_requirements(
                offered_courses,
                completed_courses
            )
            recommended.update(degree_recs)

        # prerequisites
        recommended = [
            course for course in recommended
            if self.prereq_service.prereqs_satisfied(course, completed_courses)
        ]

        # gives schedule within a 15-credit-hour target
        recommended = recommended[:5]

        return recommended
