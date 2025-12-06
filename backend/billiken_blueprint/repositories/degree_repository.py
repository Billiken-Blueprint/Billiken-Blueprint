import json
import os
from sqlalchemy import select
from typing import Sequence
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.orm import mapped_column, Mapped

from billiken_blueprint.base import Base
from billiken_blueprint.domain.degrees.degree import Degree
from billiken_blueprint.domain.degrees.degree_requirement import DegreeRequirement


os.makedirs("data/degree_requirements", exist_ok=True)


class DBDegree(Base):
    __tablename__ = "degrees"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    degree_works_major_code: Mapped[str] = mapped_column()
    degree_works_degree_type: Mapped[str] = mapped_column()
    degree_works_college_code: Mapped[str] = mapped_column()

    def to_domain(self, requirements: Sequence[DegreeRequirement]) -> Degree:
        return Degree(
            id=self.id,
            name=self.name,
            degree_works_major_code=self.degree_works_major_code,
            degree_works_degree_type=self.degree_works_degree_type,
            degree_works_college_code=self.degree_works_college_code,
            requirements=requirements,
        )


class DegreeRepository:
    def __init__(self, async_sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self.async_sessionmaker = async_sessionmaker

    async def get_requirements_for_degree(self, id: int):
        fname = f"data/degree_requirements/{id}.json"
        if not os.path.exists(fname):
            raise ValueError(f"No requirements found for degree ID {id}")
        with open(fname, "r") as f:
            data = json.load(f)
        reqs = [DegreeRequirement.from_dict(req) for req in data]
        return reqs

    async def get_by_id(self, id: int) -> Degree:
        async with self.async_sessionmaker() as session:
            db_degree = await session.get(DBDegree, id)
            if db_degree is None:
                raise ValueError(f"Degree with ID {id} not found")
            requirements = await self.get_requirements_for_degree(id)
            return db_degree.to_domain(requirements)

    async def save_requirements_for_degree(
        self, id: int, requirements: Sequence[DegreeRequirement]
    ):
        fname = f"data/degree_requirements/{id}.json"
        with open(fname, "w") as f:
            data = [req.to_dict() for req in requirements]
            json.dump(data, f, indent=2)

    async def get_all(self) -> Sequence[Degree]:
        stmt = select(DBDegree)
        async with self.async_sessionmaker() as session:
            result = await session.execute(stmt)
            degrees = result.scalars().all()
            return [
                degree.to_domain(await self.get_requirements_for_degree(degree.id))
                for degree in degrees
            ]

    async def save(self, degree: Degree) -> Degree:
        async with self.async_sessionmaker() as session:
            db_degree = None
            if degree.id is not None:
                db_degree = await session.get(DBDegree, degree.id)
            if db_degree is not None:
                # Update existing degree
                db_degree.name = degree.name
                db_degree.degree_works_major_code = degree.degree_works_major_code
                db_degree.degree_works_degree_type = degree.degree_works_degree_type
                db_degree.degree_works_college_code = degree.degree_works_college_code
            else:
                # Create new degree
                db_degree = DBDegree(
                    id=degree.id,
                    name=degree.name,
                    degree_works_major_code=degree.degree_works_major_code,
                    degree_works_degree_type=degree.degree_works_degree_type,
                    degree_works_college_code=degree.degree_works_college_code,
                )
                session.add(db_degree)
            await session.commit()

            await self.save_requirements_for_degree(db_degree.id, degree.requirements)
            return db_degree.to_domain(degree.requirements)
