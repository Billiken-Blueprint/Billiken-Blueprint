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
    code: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()


class CourseRepository:
    def __init__(self, async_sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self._async_sessionmaker = async_sessionmaker

    async def save(self, course: Course) -> Course:
        """Save or update a course in the database and return the persisted course."""
        insert_stmt = insert(DBCourse).values(
            id=course.id,
            code=course.course_code,
            name=f"{course.major} {course.course_number}",
            description=f"{course.credits} credits",
        )
        conflict_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[DBCourse.id],
            set_=dict(
                code=insert_stmt.excluded.code,
                name=insert_stmt.excluded.name,
                description=insert_stmt.excluded.description,
            ),
        ).returning(DBCourse)

        async with self._async_sessionmaker() as session:
            result = await session.execute(conflict_stmt)
            await session.commit()
            db_course = result.scalar_one()
            return self._to_domain(db_course)  # type: ignore

    async def get_by_id(self, course_id: int) -> Optional[Course]:
        """Retrieve a course by its ID."""
        stmt = select(DBCourse).where(DBCourse.id == course_id)

        async with self._async_sessionmaker() as session:
            result = await session.execute(stmt)
            db_course = result.scalar_one_or_none()

        if db_course is None:
            return None

        return self._to_domain(db_course)

    async def get_by_code(self, course_code: str) -> Optional[Course]:
        """Retrieve a course by its course code."""
        stmt = select(DBCourse).where(DBCourse.code == course_code)

        async with self._async_sessionmaker() as session:
            result = await session.execute(stmt)
            db_course = result.scalar_one_or_none()

        if db_course is None:
            return None

        return self._to_domain(db_course)

    async def get_all(self) -> list[Course]:
        """Retrieve all courses from the database."""
        stmt = select(DBCourse)

        async with self._async_sessionmaker() as session:
            result = await session.execute(stmt)
            db_courses = result.scalars().all()

        return [self._to_domain(db_course) for db_course in db_courses]

    async def delete(self, course_id: int) -> None:
        """Delete a course by its ID."""
        async with self._async_sessionmaker() as session:
            db_course = await session.get(DBCourse, course_id)
            if db_course is not None:
                await session.delete(db_course)
                await session.commit()

    async def search_by_major(self, major: str) -> list[Course]:
        """Search for courses by major prefix in the code."""
        stmt = select(DBCourse).where(DBCourse.code.like(f"{major}-%"))

        async with self._async_sessionmaker() as session:
            result = await session.execute(stmt)
            db_courses = result.scalars().all()

        return [self._to_domain(db_course) for db_course in db_courses]

    def _to_domain(self, db_course: DBCourse) -> Course:
        """Convert a DBCourse to a domain Course."""
        # Parse the code to extract major and course number
        # Assuming format like "CSCI-1050"
        parts = db_course.code.split("-")
        major = parts[0] if len(parts) > 0 else ""
        course_number = parts[1] if len(parts) > 1 else ""

        # Parse credits from description
        # Assuming format like "3 credits"
        credits = 0
        try:
            credits = int(db_course.description.split()[0])
        except (ValueError, IndexError):
            credits = 0

        return Course(
            id=db_course.id,
            major=major,
            course_number=course_number,
            course_code=db_course.code,
            credits=credits,
        )
