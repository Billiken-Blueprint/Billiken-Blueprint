from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column

from courses_scraping.persistence.base import Base


class Course(Base):
    __tablename__ = 'Courses'

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(nullable=False, unique=True)
    title: Mapped[str] = mapped_column(nullable=False)
