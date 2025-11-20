import sqlalchemy
from billiken_blueprint.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from typing import TYPE_CHECKING

from billiken_blueprint.courses_at_slu.section import Section
from billiken_blueprint.repositories.instructor_section_association import (
    instructor_sections_association,
)

if TYPE_CHECKING:
    from billiken_blueprint.repositories.instructor_repository import DBInstructor

from sqlalchemy.dialects.sqlite import insert


class DBCourseSection(Base):
    __tablename__ = "course_sections"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column()
    crn: Mapped[str] = mapped_column()
    instructors: Mapped[list["DBInstructor"]] = relationship(
        secondary=instructor_sections_association,
        back_populates="sections",
        lazy="select",
    )


class CourseSectionRepository:
    def __init__(self, async_sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self._async_sessionmaker = async_sessionmaker

    async def save(
        self,
        course_section: Section,
        course_id: int,
        crn: str,
        instructor_ids: list[int],
    ) -> DBCourseSection:
        """Save or update a course section and return the persisted section."""
        # First, insert or update the course section itself
        insert_stmt = insert(DBCourseSection).values(
            course_id=course_id,
            crn=crn,
        )
        conflict_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[DBCourseSection.id],  # Assuming CRN is unique
            set_=dict(
                course_id=insert_stmt.excluded.course_id,
            ),
        ).returning(DBCourseSection)

        async with self._async_sessionmaker() as session:
            result = await session.execute(conflict_stmt)
            db_section = result.scalar_one()
            section_id = db_section.id
            await session.commit()

            # Now handle the many-to-many relationship with instructors
            # First, delete existing associations for this section
            delete_stmt = sqlalchemy.delete(instructor_sections_association).where(
                instructor_sections_association.c.section_id == section_id
            )
            await session.execute(delete_stmt)

            # Insert new associations
            if instructor_ids:
                for instructor_id in instructor_ids:
                    assoc_insert = insert(instructor_sections_association).values(
                        instructor_id=instructor_id,
                        section_id=section_id,
                    )
                    await session.execute(assoc_insert)

            await session.commit()
            return db_section  # type: ignore
