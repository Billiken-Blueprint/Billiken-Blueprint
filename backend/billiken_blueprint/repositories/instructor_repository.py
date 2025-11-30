from typing import Optional, TYPE_CHECKING
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy import Column, ForeignKey, Table, select
from billiken_blueprint.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from billiken_blueprint.domain.instructor import Professor
from billiken_blueprint.repositories.course_repository import DBCourse


class DBInstructor(Base):
    __tablename__ = "instructors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    rmp_rating: Mapped[Optional[float]] = mapped_column(nullable=True)
    rmp_num_ratings: Mapped[Optional[int]] = mapped_column(nullable=True)
    rmp_url: Mapped[Optional[str]] = mapped_column(nullable=True)
    department: Mapped[Optional[str]] = mapped_column(nullable=True)


class InstructorRepository:
    def __init__(self, async_sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self._async_sessionmaker = async_sessionmaker

    async def save(self, instructor: Professor) -> Professor:
        """Save or update an instructor in the database and return the persisted instructor."""
        insert_stmt = insert(DBInstructor).values(
            id=instructor.id,
            name=instructor.name,
            rmp_rating=instructor.rmp_rating,
            rmp_num_ratings=instructor.rmp_num_ratings,
            rmp_url=instructor.rmp_url,
            department=instructor.department,
        )
        conflict_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[DBInstructor.id],
            set_=dict(
                name=insert_stmt.excluded.name,
                rmp_rating=insert_stmt.excluded.rmp_rating,
                rmp_num_ratings=insert_stmt.excluded.rmp_num_ratings,
                rmp_url=insert_stmt.excluded.rmp_url,
                department=insert_stmt.excluded.department,
            ),
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
            Professor(
                id=db_instructor.id,
                name=db_instructor.name,
                rmp_rating=getattr(db_instructor, "rmp_rating", None),
                rmp_num_ratings=getattr(db_instructor, "rmp_num_ratings", None),
                rmp_url=getattr(db_instructor, "rmp_url", None),
                department=getattr(db_instructor, "department", None),
            )
            for db_instructor in db_instructors
        ]

    async def get_by_id(self, instructor_id: int) -> Optional[Professor]:
        async with self._async_sessionmaker() as session:
            db_instructor = await session.get(DBInstructor, instructor_id)
            if db_instructor:
                return Professor(
                    id=db_instructor.id,
                    name=db_instructor.name,
                    rmp_rating=getattr(db_instructor, "rmp_rating", None),
                    rmp_num_ratings=getattr(db_instructor, "rmp_num_ratings", None),
                    rmp_url=getattr(db_instructor, "rmp_url", None),
                    department=getattr(db_instructor, "department", None),
                )
        return None

    async def get_by_name(self, name: str) -> Optional[Professor]:
        stmt = select(DBInstructor).where(DBInstructor.name == name)

        async with self._async_sessionmaker() as session:
            result = await session.execute(stmt)
            db_instructor = result.scalar_one_or_none()

        if db_instructor:
            return Professor(
                id=db_instructor.id,
                name=db_instructor.name,
                rmp_rating=getattr(db_instructor, "rmp_rating", None),
                rmp_num_ratings=getattr(db_instructor, "rmp_num_ratings", None),
                rmp_url=getattr(db_instructor, "rmp_url", None),
                department=getattr(db_instructor, "department", None),
            )
        return None
