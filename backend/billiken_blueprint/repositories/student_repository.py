from os import major, minor, name
from typing import Optional
from sqlalchemy import JSON
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from billiken_blueprint.base import Base
from billiken_blueprint.domain.student import Student, TimeSlot


class DBStudent(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    completed_course_ids: Mapped[list[int]] = mapped_column(JSON)
    desired_course_ids: Mapped[list[int]] = mapped_column(JSON, default=[])
    unavailability_times: Mapped[list[dict]] = mapped_column(JSON, default=[])
    avoid_times: Mapped[list[dict]] = mapped_column(JSON, default=[])

    graduation_year: Mapped[int] = mapped_column()
    degree_id: Mapped[int] = mapped_column(default=1)

    def to_domain(self) -> Student:
        """Convert DBStudent to Student domain object."""
        return Student(
            id=self.id,
            name=self.name,
            completed_course_ids=self.completed_course_ids,
            desired_course_ids=self.desired_course_ids,
            unavailability_times=[TimeSlot.from_dict(d) for d in self.unavailability_times],
            avoid_times=[TimeSlot.from_dict(d) for d in self.avoid_times],
            degree_id=self.degree_id,
            graduation_year=self.graduation_year,
        )


class StudentRepository:
    def __init__(self, async_sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self._async_sessionmaker = async_sessionmaker

    async def save(self, student: Student) -> Student:
        insert_stmt = insert(DBStudent).values(
            id=student.id,
            name=student.name,
            completed_course_ids=student.completed_course_ids,
            desired_course_ids=student.desired_course_ids,
            unavailability_times=[ts.to_dict() for ts in student.unavailability_times],
            avoid_times=[ts.to_dict() for ts in student.avoid_times],
            degree_id=student.degree_id,
            graduation_year=student.graduation_year,
        )
        conflict_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[DBStudent.id],
            set_=dict(
                name=insert_stmt.excluded.name,
                completed_course_ids=insert_stmt.excluded.completed_course_ids,
                desired_course_ids=insert_stmt.excluded.desired_course_ids,
                unavailability_times=insert_stmt.excluded.unavailability_times,
                avoid_times=insert_stmt.excluded.avoid_times,
                graduation_year=insert_stmt.excluded.graduation_year,
                degree_id=insert_stmt.excluded.degree_id,
            ),
        ).returning(DBStudent)

        async with self._async_sessionmaker() as session:
            result = await session.execute(conflict_stmt)
            await session.commit()
            db_student: DBStudent = result.scalar_one()  # type: ignore
            return db_student.to_domain()

    async def get_by_id(self, student_id: int) -> Optional[Student]:
        async with self._async_sessionmaker() as session:
            result = await session.get(DBStudent, student_id)
            if result is None:
                return None
            return result.to_domain()
