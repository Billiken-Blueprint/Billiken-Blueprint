from os import name
from typing import Optional
from sqlalchemy import JSON
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from billiken_blueprint.base import Base
from billiken_blueprint.domain.student import Student


class DBStudent(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    degree_ids: Mapped[list[int]] = mapped_column(JSON)
    completed_course_ids: Mapped[list[int]] = mapped_column(JSON)


class StudentRepository:
    def __init__(self, async_sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self._async_sessionmaker = async_sessionmaker

    async def save(self, student: Student) -> DBStudent:
        insert_stmt = insert(DBStudent).values(
            id=student.id,
            name=student.name,
            degree_ids=student.degree_ids,
            completed_course_ids=student.completed_course_ids,
        )
        conflict_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[DBStudent.id],
            set_=dict(
                name=insert_stmt.excluded.name,
                degree_ids=insert_stmt.excluded.degree_ids,
                completed_course_ids=insert_stmt.excluded.completed_course_ids,
            ),
        ).returning(DBStudent)

        async with self._async_sessionmaker() as session:
            result = await session.execute(conflict_stmt)
            await session.commit()
            return result.scalar_one()  # type: ignore

    async def get_by_id(self, student_id: int) -> Optional[Student]:
        async with self._async_sessionmaker() as session:
            result = await session.get(DBStudent, student_id)
            if result is None:
                return None
            return Student(
                id=result.id,
                name=result.name,
                degree_ids=result.degree_ids,
                completed_course_ids=result.completed_course_ids,
            )
