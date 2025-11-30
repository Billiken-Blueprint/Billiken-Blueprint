from billiken_blueprint.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from billiken_blueprint.domain.courses.course_attribute import CourseAttribute


class DBCourseAttribute(Base):
    __tablename__ = "course_attributes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    degree_works_label: Mapped[str] = mapped_column(nullable=False, unique=True)
    courses_at_slu_label: Mapped[str] = mapped_column(nullable=False, unique=True)

    def to_domain(self) -> CourseAttribute:
        return CourseAttribute(
            id=self.id,
            name=self.name,
            degree_works_label=self.degree_works_label,
            courses_at_slu_label=self.courses_at_slu_label,
        )


class CourseAttributeRepository:
    def __init__(self, async_sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self.async_sessionmaker = async_sessionmaker

    async def get_by_id(self, attribute_id: int) -> CourseAttribute:
        async with self.async_sessionmaker() as session:
            db_attribute = await session.get(DBCourseAttribute, attribute_id)
            if db_attribute is None:
                raise ValueError(f"CourseAttribute with id {attribute_id} not found")
            return db_attribute.to_domain()

    async def save(self, attribute: CourseAttribute) -> CourseAttribute:
        async with self.async_sessionmaker() as session:
            db_attribute = None
            if attribute.id is not None:
                db_attribute = await session.get(DBCourseAttribute, attribute.id)
            if db_attribute is not None:
                # Update existing attribute
                db_attribute.name = attribute.name
                db_attribute.degree_works_label = attribute.degree_works_label
                db_attribute.courses_at_slu_label = attribute.courses_at_slu_label
            else:
                # Create new attribute
                db_attribute = DBCourseAttribute(
                    id=attribute.id,
                    name=attribute.name,
                    degree_works_label=attribute.degree_works_label,
                    courses_at_slu_label=attribute.courses_at_slu_label,
                )
                session.add(db_attribute)
            await session.commit()
            await session.refresh(db_attribute)
            return db_attribute.to_domain()
