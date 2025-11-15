from typing import Optional
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from billiken_blueprint.base import Base
from billiken_blueprint.domain.course import Course


class DBCourse(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(index=True, unique=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()

    def to_course(self) -> Course:
        return Course(
            id=self.id,
            course_code=self.code,
            title=self.name,
            description=self.description,
            major=self.code.split()[0],
            course_number=self.code.split()[1],
        )


class CourseRepository:
    def __init__(self, async_sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self._async_sessionmaker = async_sessionmaker

    async def save(self, course: Course) -> DBCourse:
        """Save or update a course in the database and return the persisted course."""
        insert_stmt = insert(DBCourse).values(
            id=course.id,
            code=course.course_code,
            name=course.title,
            description=course.description,
        )
        conflict_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[DBCourse.code],
            set_=dict(
                name=insert_stmt.excluded.name,
                description=insert_stmt.excluded.description,
            ),
        ).returning(DBCourse)

        async with self._async_sessionmaker() as session:
            result = await session.execute(conflict_stmt)
            await session.commit()
            db_course = result.scalar_one()
            return db_course

    async def get_all(self) -> list[Course]:
        """Retrieve all courses from the database."""
        stmt = select(DBCourse)

        async with self._async_sessionmaker() as session:
            result = await session.execute(stmt)
            db_courses = result.scalars().all()

        return [db_course.to_course() for db_course in db_courses]

    async def get_by_code(self, course_code: str) -> Optional[DBCourse]:
        """Retrieve a course by its course code."""
        stmt = select(DBCourse).where(DBCourse.code == course_code)

        async with self._async_sessionmaker() as session:
            result = await session.execute(stmt)
            db_course = result.scalar_one_or_none()

        if db_course is None:
            return None

        return db_course

    async def get_by_id(self, course_id: int) -> Optional[DBCourse]:
        """Retrieve a course by its ID."""
        stmt = select(DBCourse).where(DBCourse.id == course_id)

        async with self._async_sessionmaker() as session:
            result = await session.execute(stmt)
            db_course = result.scalar_one_or_none()

        if db_course is None:
            return None

        return db_course

    async def delete(self, course_id: int) -> None:
        """Delete a course by its ID."""
        async with self._async_sessionmaker() as session:
            db_course = await session.get(DBCourse, course_id)
            if db_course is not None:
                await session.delete(db_course)
                await session.commit()
