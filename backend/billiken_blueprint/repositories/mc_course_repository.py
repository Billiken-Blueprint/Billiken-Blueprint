from sqlalchemy import JSON
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column


from billiken_blueprint.base import Base


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
