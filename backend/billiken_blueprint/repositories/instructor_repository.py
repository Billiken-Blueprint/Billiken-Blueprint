from typing import Optional, TYPE_CHECKING
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy import Column, ForeignKey, Table, select
from billiken_blueprint.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from billiken_blueprint.domain.instructor import Professor
from billiken_blueprint.repositories.course_repository import DBCourse
from billiken_blueprint.repositories.instructor_section_association import (
    instructor_sections_association,
)

if TYPE_CHECKING:
    from billiken_blueprint.repositories.course_section_repository import (
        DBCourseSection,
    )


class DBInstructor(Base):
    __tablename__ = "instructors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    sections: Mapped[list["DBCourseSection"]] = relationship(
        secondary=instructor_sections_association,
        back_populates="instructors",
        lazy="select",
    )


class InstructorRepository:
    def __init__(self, async_sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self._async_sessionmaker = async_sessionmaker

    async def save(self, instructor: Professor) -> Professor:
        """Save or update an instructor in the database and return the persisted instructor."""
        insert_stmt = insert(DBInstructor).values(
            id=instructor.id, name=instructor.name
        )
        conflict_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[DBInstructor.id],
            set_=dict(name=insert_stmt.excluded.name),
        ).returning(DBInstructor)

        async with self._async_sessionmaker() as session:
            result = await session.execute(conflict_stmt)
            await session.commit()
            db_instructor = result.scalar_one()
            return Professor(id=db_instructor.id, name=db_instructor.name)  # type: ignore

    async def get_all(self) -> list[Professor]:
        """Retrieve all instructors from the database."""
        stmt = select(DBInstructor)

        async with self._async_sessionmaker() as session:
            result = await session.execute(stmt)
            db_instructors = result.scalars().all()

        return [
            Professor(id=db_instructor.id, name=db_instructor.name)
            for db_instructor in db_instructors
        ]

    async def get_by_name(self, name: str) -> Optional[Professor]:
        stmt = select(DBInstructor).where(DBInstructor.name == name)

        async with self._async_sessionmaker() as session:
            result = await session.execute(stmt)
            db_instructor = result.scalar_one_or_none()

        if db_instructor:
            return Professor(id=db_instructor.id, name=db_instructor.name)
        return None
