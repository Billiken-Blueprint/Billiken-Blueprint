from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column

from courses_scraping.persistence.base import Base


class Instructor(Base):
    __tablename__ = 'Instructors'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
