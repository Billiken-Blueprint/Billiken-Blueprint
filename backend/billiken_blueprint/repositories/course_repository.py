import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import JSON, select

from billiken_blueprint.base import Base
from billiken_blueprint.domain.courses.course import Course
from billiken_blueprint.domain.courses.course_prerequisite import (
    NestedCoursePrerequisite,
)


class DBCourse(Base):
    __tablename__ = "courses"

    __table_args__ = (
        sqlalchemy.UniqueConstraint(
            "major_code", "course_number", name="uix_major_course_number"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    attribute_ids: Mapped[list[int]] = mapped_column(JSON, nullable=False)
    prerequisites: Mapped[dict] = mapped_column(JSON, nullable=True)
    major_code: Mapped[str] = mapped_column(nullable=False)
    course_number: Mapped[str] = mapped_column(nullable=False)

    def to_domain(self) -> Course:
        return Course(
            id=self.id,
            attribute_ids=self.attribute_ids,
            prerequisites=(
                NestedCoursePrerequisite.from_dict(self.prerequisites)
                if self.prerequisites
                else None
            ),
            major_code=self.major_code,
            course_number=self.course_number,
        )


class CourseRepository:
    def __init__(self, async_sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self.async_sessionmaker = async_sessionmaker

    async def save(self, course: Course) -> Course:
        async with self.async_sessionmaker() as session:
            db_course = None
            if course.id is not None:
                db_course = await session.get(DBCourse, course.id)
            if db_course is not None:
                # Update existing course
                db_course.attribute_ids = course.attribute_ids
                db_course.prerequisites = (
                    course.prerequisites.to_dict() if course.prerequisites else None
                )  # type: ignore
                db_course.major_code = course.major_code
                db_course.course_number = course.course_number
            else:
                # Create new course
                db_course = DBCourse(
                    id=course.id,
                    attribute_ids=course.attribute_ids,
                    prerequisites=(
                        course.prerequisites.to_dict() if course.prerequisites else None
                    ),
                    major_code=course.major_code,
                    course_number=course.course_number,
                )
                session.add(db_course)
            await session.commit()
            return db_course.to_domain()

    async def get_by_id(self, course_id: int) -> Course | None:
        async with self.async_sessionmaker() as session:
            db_course = await session.get(DBCourse, course_id)
            if db_course is None:
                return None
            return db_course.to_domain()

    async def get_by_code(self, course_code: str) -> Course | None:
        """Retrieve a course by its code (e.g., 'CSCI 1000')."""
        major_code, course_number = course_code.split()
        async with self.async_sessionmaker() as session:
            result = await session.execute(
                select(DBCourse)
                .where(
                    DBCourse.major_code == major_code,
                    DBCourse.course_number == course_number,
                )
                .limit(1)
            )
            db_course = result.scalars().first()
            if db_course is None:
                return None
            return db_course.to_domain()

    async def get_all(self) -> list[Course]:
        async with self.async_sessionmaker() as session:
            result = await session.execute(select(DBCourse))
            db_courses = result.scalars().all()
            return [db_course.to_domain() for db_course in db_courses]
