import select
from typing import Optional
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy import delete, desc, select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from billiken_blueprint.base import Base
from billiken_blueprint.domain.rating import Rating


class DBRating(Base):
    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[Optional[int]] = mapped_column(nullable=True, index=True)
    professor_id: Mapped[Optional[int]] = mapped_column(nullable=True, index=True)
    student_id: Mapped[int] = mapped_column(nullable=False, index=True)
    rating_value: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)

    def to_rating(self) -> Rating:
        return Rating(
            id=self.id,
            course_id=self.course_id,
            professor_id=self.professor_id,
            student_id=self.student_id,
            rating_value=self.rating_value,
            description=self.description,
        )


class RatingRepository:
    def __init__(self, async_sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self._async_sessionmaker = async_sessionmaker

    async def save(self, rating: Rating) -> Rating:
        """Save or update a rating in the database and return the persisted rating."""
        insert_stmt = insert(DBRating).values(
            id=rating.id,
            course_id=rating.course_id,
            professor_id=rating.professor_id,
            student_id=rating.student_id,
            rating_value=rating.rating_value,
            description=rating.description,
        )
        conflict_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[DBRating.id],
            set_=dict(
                course_id=insert_stmt.excluded.course_id,
                professor_id=insert_stmt.excluded.professor_id,
                student_id=insert_stmt.excluded.student_id,
                rating_value=insert_stmt.excluded.rating_value,
                description=insert_stmt.excluded.description,
            ),
        ).returning(DBRating)

        async with self._async_sessionmaker() as session:
            result = await session.execute(conflict_stmt)
            await session.commit()
            return result.scalar_one().to_rating()

    async def get_all(
        self, instructor_id: Optional[int] = None, course_id: Optional[int] = None
    ) -> list[Rating]:
        """Retrieve all ratings from the database, optionally filtered by instructor or course."""
        stmt = select(DBRating)
        if instructor_id is not None:
            stmt = stmt.where(DBRating.professor_id == instructor_id)
        if course_id is not None:
            stmt = stmt.where(DBRating.course_id == course_id)

        async with self._async_sessionmaker() as session:
            result = await session.execute(stmt)
            db_ratings = result.scalars().all()

        return [db_rating.to_rating() for db_rating in db_ratings]

    async def delete(self, rating_id: int) -> None:
        """Delete a rating by its ID."""
        delete_stmt = delete(DBRating).where(DBRating.id == rating_id)

        async with self._async_sessionmaker() as session:
            await session.execute(delete_stmt)
            await session.commit()
