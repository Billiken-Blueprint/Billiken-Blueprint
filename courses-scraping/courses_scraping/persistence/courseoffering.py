from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.testing.schema import mapped_column

from courses_scraping.persistence.base import Base
from courses_scraping.persistence.instructor import Instructor


class CourseOffering(Base):
    __tablename__ = 'CourseOfferings'

    id: Mapped[int] = mapped_column(primary_key=True)
    semester: Mapped[str] = mapped_column(nullable=False)
    crn: Mapped[str] = mapped_column(nullable=False)
    instructors: Mapped[list[Instructor]] = relationship()
    course_id: Mapped[int] = mapped_column(ForeignKey('Courses.id'), primary_key=True)
