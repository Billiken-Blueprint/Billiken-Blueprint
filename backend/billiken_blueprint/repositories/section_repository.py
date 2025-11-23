import sqlalchemy
from billiken_blueprint.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import JSON

from billiken_blueprint.domain.section import Section, MeetingTime


class SectionRepositoryDBEntity(Base):
    __tablename__ = "sections"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    crn: Mapped[str] = mapped_column()
    instructor_names: Mapped[list[str]] = mapped_column(JSON)
    campus_code: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    title: Mapped[str] = mapped_column()
    course_code: Mapped[str] = mapped_column()
    semester: Mapped[str] = mapped_column()
    meeting_times: Mapped[list[dict]] = mapped_column(JSON)

    def to_domain(self) -> Section:
        return Section(
            id=self.id,
            crn=self.crn,
            instructor_names=self.instructor_names,
            campus_code=self.campus_code,
            description=self.description,
            title=self.title,
            course_code=self.course_code,
            semester=self.semester,
            meeting_times=[
                MeetingTime(
                    day=mt["day"],
                    start_time=mt["start_time"],
                    end_time=mt["end_time"],
                )
                for mt in self.meeting_times
            ],
        )


class SectionRepository:
    def __init__(self, async_sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self.async_sessionmaker = async_sessionmaker

    async def save(self, section: Section) -> Section:
        async with self.async_sessionmaker() as session:
            db_entity = None
            if section.id is not None:
                db_entity = await session.get(SectionRepositoryDBEntity, section.id)

            if db_entity is None:
                stmt = sqlalchemy.select(SectionRepositoryDBEntity).where(
                    SectionRepositoryDBEntity.crn == section.crn,
                    SectionRepositoryDBEntity.semester == section.semester,
                )
                result = await session.execute(stmt)
                db_entity = result.scalar_one_or_none()

            if db_entity:
                db_entity.crn = section.crn
                db_entity.instructor_names = section.instructor_names
                db_entity.campus_code = section.campus_code
                db_entity.description = section.description
                db_entity.title = section.title
                db_entity.course_code = section.course_code
                db_entity.semester = section.semester
                db_entity.meeting_times = [
                    {
                        "day": mt.day,
                        "start_time": mt.start_time,
                        "end_time": mt.end_time,
                    }
                    for mt in section.meeting_times
                ]
            else:
                db_entity = SectionRepositoryDBEntity(
                    crn=section.crn,
                    instructor_names=section.instructor_names,
                    campus_code=section.campus_code,
                    description=section.description,
                    title=section.title,
                    course_code=section.course_code,
                    semester=section.semester,
                    meeting_times=[
                        {
                            "day": mt.day,
                            "start_time": mt.start_time,
                            "end_time": mt.end_time,
                        }
                        for mt in section.meeting_times
                    ],
                )
                session.add(db_entity)

            await session.commit()
            await session.refresh(db_entity)

            return db_entity.to_domain()

    async def get_all(self) -> list[Section]:
        async with self.async_sessionmaker() as session:
            result = await session.execute(sqlalchemy.select(SectionRepositoryDBEntity))
            db_entities = result.scalars().all()
            return [db_entity.to_domain() for db_entity in db_entities]

    async def get_all_for_semester(self, semester: str) -> list[Section]:
        async with self.async_sessionmaker() as session:
            stmt = sqlalchemy.select(SectionRepositoryDBEntity).where(
                SectionRepositoryDBEntity.semester == semester
            )
            result = await session.execute(stmt)
            db_entities = result.scalars().all()
            return [db_entity.to_domain() for db_entity in db_entities]

    async def get_by_course_code_and_semester(
        self, code: str, semester: str
    ) -> list[Section]:
        async with self.async_sessionmaker() as session:
            stmt = sqlalchemy.select(SectionRepositoryDBEntity).where(
                SectionRepositoryDBEntity.course_code == code,
                SectionRepositoryDBEntity.semester == semester,
            )
            result = await session.execute(stmt)
            db_entities = result.scalars().all()
            return [db_entity.to_domain() for db_entity in db_entities]
