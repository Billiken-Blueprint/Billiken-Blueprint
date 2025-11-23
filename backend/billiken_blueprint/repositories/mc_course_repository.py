from sqlalchemy import JSON
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column


from billiken_blueprint.base import Base
from billiken_blueprint.domain.course import MinimalCourse
from billiken_blueprint.domain.course_attribute import CourseAttribute, CourseAttributes


class MCCourseDbEntity(Base):
    __tablename__ = "mc_courses"

    __table_args__ = (
        sqlalchemy.UniqueConstraint(
            "major_code", "course_number", name="uix_major_course_number"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    major_code: Mapped[str] = mapped_column()
    course_number: Mapped[str] = mapped_column()
    attributes: Mapped[list[str]] = mapped_column(JSON)

    def to_domain(self) -> MinimalCourse:
        return MinimalCourse(
            id=self.id,
            major_code=self.major_code,
            course_number=self.course_number,
            attributes=[
                ca
                for ca in vars(CourseAttributes).values()
                if isinstance(ca, CourseAttribute) and ca.name in self.attributes
            ],
        )


class MCCourseRepository:
    def __init__(self, async_sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self.async_sessionmaker = async_sessionmaker

    async def save(self, course: MinimalCourse) -> MinimalCourse:
        async with self.async_sessionmaker() as session:
            db_entity = None
            if course.id is not None:
                db_entity = await session.get(MCCourseDbEntity, course.id)

            if db_entity is None:
                stmt = sqlalchemy.select(MCCourseDbEntity).where(
                    MCCourseDbEntity.major_code == course.major_code,
                    MCCourseDbEntity.course_number == course.course_number,
                )
                result = await session.execute(stmt)
                db_entity = result.scalar_one_or_none()

            if db_entity:
                db_entity.major_code = course.major_code
                db_entity.course_number = course.course_number
                db_entity.attributes = [attr.name for attr in course.attributes]
            else:
                db_entity = MCCourseDbEntity(
                    id=course.id,
                    major_code=course.major_code,
                    course_number=course.course_number,
                    attributes=[attr.name for attr in course.attributes],
                )
                session.add(db_entity)

            await session.commit()
            await session.refresh(db_entity)
            return db_entity.to_domain()

    async def get_by_code(
        self, major_code: str, course_number: str
    ) -> MinimalCourse | None:
        async with self.async_sessionmaker() as session:
            stmt = sqlalchemy.select(MCCourseDbEntity).where(
                MCCourseDbEntity.major_code == major_code,
                MCCourseDbEntity.course_number == course_number,
            )
            result = await session.execute(stmt)
            db_entity = result.scalar_one_or_none()
            if db_entity:
                return db_entity.to_domain()
            return None

    async def get_all(self) -> list[MinimalCourse]:
        async with self.async_sessionmaker() as session:
            result = await session.execute(sqlalchemy.select(MCCourseDbEntity))
            db_entities = result.scalars().all()
            return [db_entity.to_domain() for db_entity in db_entities]
