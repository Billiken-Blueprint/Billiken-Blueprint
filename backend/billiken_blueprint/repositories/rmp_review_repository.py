from typing import Optional
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy import select, delete, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from datetime import datetime

from billiken_blueprint.base import Base
from billiken_blueprint.domain.rmp_review import RmpReview


class DBRmpReview(Base):
    __tablename__ = "rmp_reviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    instructor_id: Mapped[int] = mapped_column(nullable=False, index=True)
    course: Mapped[Optional[str]] = mapped_column(nullable=True)
    course_id: Mapped[Optional[int]] = mapped_column(nullable=True, index=True)
    quality: Mapped[float] = mapped_column(nullable=False)
    difficulty: Mapped[Optional[float]] = mapped_column(nullable=True)
    comment: Mapped[str] = mapped_column(nullable=False)
    would_take_again: Mapped[Optional[bool]] = mapped_column(nullable=True)
    grade: Mapped[Optional[str]] = mapped_column(nullable=True)
    attendance: Mapped[Optional[str]] = mapped_column(nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    review_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    def to_rmp_review(self) -> RmpReview:
        return RmpReview(
            id=self.id,
            instructor_id=self.instructor_id,
            course=self.course,
            course_id=getattr(self, 'course_id', None),
            quality=self.quality,
            difficulty=self.difficulty,
            comment=self.comment,
            would_take_again=self.would_take_again,
            grade=self.grade,
            attendance=self.attendance,
            tags=self.tags or [],
            review_date=self.review_date,
        )


class RmpReviewRepository:
    def __init__(self, async_sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self._async_sessionmaker = async_sessionmaker

    async def save(self, review: RmpReview) -> RmpReview:
        """Save or update an RMP review in the database."""
        insert_stmt = insert(DBRmpReview).values(
            id=review.id,
            instructor_id=review.instructor_id,
            course=review.course,
            course_id=review.course_id,
            quality=review.quality,
            difficulty=review.difficulty,
            comment=review.comment,
            would_take_again=review.would_take_again,
            grade=review.grade,
            attendance=review.attendance,
            tags=review.tags,
            review_date=review.review_date,
        )
        conflict_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[DBRmpReview.id],
            set_=dict(
                instructor_id=insert_stmt.excluded.instructor_id,
                course=insert_stmt.excluded.course,
                course_id=insert_stmt.excluded.course_id,
                quality=insert_stmt.excluded.quality,
                difficulty=insert_stmt.excluded.difficulty,
                comment=insert_stmt.excluded.comment,
                would_take_again=insert_stmt.excluded.would_take_again,
                grade=insert_stmt.excluded.grade,
                attendance=insert_stmt.excluded.attendance,
                tags=insert_stmt.excluded.tags,
                review_date=insert_stmt.excluded.review_date,
            ),
        ).returning(DBRmpReview)

        async with self._async_sessionmaker() as session:
            result = await session.execute(conflict_stmt)
            await session.commit()
            return result.scalar_one().to_rmp_review()

    async def save_many(self, reviews: list[RmpReview]) -> None:
        """Save multiple RMP reviews in a single transaction."""
        if not reviews:
            return
        
        values = [
            {
                "id": review.id,
                "instructor_id": review.instructor_id,
                "course": review.course,
                "course_id": review.course_id,
                "quality": review.quality,
                "difficulty": review.difficulty,
                "comment": review.comment,
                "would_take_again": review.would_take_again,
                "grade": review.grade,
                "attendance": review.attendance,
                "tags": review.tags,
                "review_date": review.review_date,
            }
            for review in reviews
        ]
        
        insert_stmt = insert(DBRmpReview).values(values)
        conflict_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[DBRmpReview.id],
            set_=dict(
                instructor_id=insert_stmt.excluded.instructor_id,
                course=insert_stmt.excluded.course,
                course_id=insert_stmt.excluded.course_id,
                quality=insert_stmt.excluded.quality,
                difficulty=insert_stmt.excluded.difficulty,
                comment=insert_stmt.excluded.comment,
                would_take_again=insert_stmt.excluded.would_take_again,
                grade=insert_stmt.excluded.grade,
                attendance=insert_stmt.excluded.attendance,
                tags=insert_stmt.excluded.tags,
                review_date=insert_stmt.excluded.review_date,
            ),
        )

        async with self._async_sessionmaker() as session:
            await session.execute(conflict_stmt)
            await session.commit()

    async def get_by_instructor_id(self, instructor_id: int) -> list[RmpReview]:
        """Retrieve all RMP reviews for a specific instructor."""
        stmt = select(DBRmpReview).where(DBRmpReview.instructor_id == instructor_id)

        async with self._async_sessionmaker() as session:
            result = await session.execute(stmt)
            db_reviews = result.scalars().all()

        return [db_review.to_rmp_review() for db_review in db_reviews]
    
    async def get_by_course_id(self, course_id: int) -> list[RmpReview]:
        """Retrieve all RMP reviews for a specific course."""
        stmt = select(DBRmpReview).where(DBRmpReview.course_id == course_id)

        async with self._async_sessionmaker() as session:
            result = await session.execute(stmt)
            db_reviews = result.scalars().all()

        return [db_review.to_rmp_review() for db_review in db_reviews]
    
    async def get_all(self) -> list[RmpReview]:
        """Retrieve all RMP reviews."""
        stmt = select(DBRmpReview)

        async with self._async_sessionmaker() as session:
            result = await session.execute(stmt)
            db_reviews = result.scalars().all()

        return [db_review.to_rmp_review() for db_review in db_reviews]

    async def delete_by_instructor_id(self, instructor_id: int) -> None:
        """Delete all RMP reviews for a specific instructor."""
        delete_stmt = delete(DBRmpReview).where(DBRmpReview.instructor_id == instructor_id)

        async with self._async_sessionmaker() as session:
            await session.execute(delete_stmt)
            await session.commit()

