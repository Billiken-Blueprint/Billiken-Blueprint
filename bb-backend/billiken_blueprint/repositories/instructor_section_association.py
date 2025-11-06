from sqlalchemy import Column, ForeignKey, Table
from billiken_blueprint.base import Base


instructor_sections_association = Table(
    "instructor_sections",
    Base.metadata,
    Column("instructor_id", ForeignKey("instructors.id"), primary_key=True),
    Column("section_id", ForeignKey("course_sections.id"), primary_key=True),
)
