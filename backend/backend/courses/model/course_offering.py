from base.base import Base
from sqlalchemy.orm import Mapped, mapped_column


class CourseOffering(Base):
    """
    Represents a course offering for a semester. Includes
    meeting times, instructor, etc.
    """

    __tablename__ = "course_offerings"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column()
    semester: Mapped[str] = mapped_column()
    crn: Mapped[str] = mapped_column()
