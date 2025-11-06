from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from base.base import Base


class Course(Base):
    """
    Represents a course that can be offered at SLU, not an actual
    course offering.
    """

    __tablename__ = "courses"
    __table_args__ = (UniqueConstraint("code", "title", name="uq_courses_code_title"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column()
    title: Mapped[str] = mapped_column()
