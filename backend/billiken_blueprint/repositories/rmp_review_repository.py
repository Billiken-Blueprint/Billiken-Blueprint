from typing import Optional
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy import select, delete, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from datetime import datetime
from pathlib import Path
import json
import re
from functools import lru_cache

from billiken_blueprint.base import Base
from billiken_blueprint.domain.ratings.rmp_review import RmpReview


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
            course_id=getattr(self, "course_id", None),
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
    def __init__(
        self,
        async_sessionmaker: async_sessionmaker[AsyncSession],
        instructor_repo=None,
        course_repo=None,
    ) -> None:
        self._async_sessionmaker = async_sessionmaker
        self._instructor_repo = instructor_repo
        self._course_repo = course_repo
        self._rmp_data_cache = None

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

    def _load_rmp_data_from_files(self) -> list[dict]:
        """Load RMP data from JSON files."""
        if self._rmp_data_cache is not None:
            return self._rmp_data_cache

        rmp_data = []
        data_dir = Path("data_dumps")

        # Try CS professors files
        for filename in ["cs_professors_with_reviews.json", "cs_professors.json"]:
            path = data_dir / filename
            if path.exists():
                with open(path, "r") as f:
                    cs_data = json.load(f)
                    for prof in cs_data:
                        prof["_department"] = "CSCI"
                    rmp_data.extend(cs_data)
                    break

        # Try Math professors files
        for filename in [
            "math_professors_with_reviews.json",
            "math_professors.json",
        ]:
            path = data_dir / filename
            if path.exists():
                with open(path, "r") as f:
                    math_data = json.load(f)
                    for prof in math_data:
                        prof["_department"] = "MATH"
                    rmp_data.extend(math_data)
                    break

        self._rmp_data_cache = rmp_data
        return rmp_data

    def _normalize_course_code(self, course_code: str) -> str:
        """Normalize course code by removing spaces and converting to uppercase."""
        if not course_code:
            return ""
        return course_code.replace(" ", "").replace("-", "").upper()

    def _course_code_matches(self, review_course: Optional[str], target: str) -> bool:
        """Check if a review's course field matches the target course code."""
        if not review_course or not target:
            return False
        normalized_review = self._normalize_course_code(review_course)
        normalized_target = self._normalize_course_code(target)
        return normalized_target in normalized_review or normalized_review in normalized_target

    async def get_by_instructor_id(self, instructor_id: int) -> list[RmpReview]:
        """Retrieve all RMP reviews for a specific instructor.
        
        First tries database, then falls back to JSON files if database is empty.
        """
        # Try database first (for backward compatibility)
        stmt = select(DBRmpReview).where(DBRmpReview.instructor_id == instructor_id)

        async with self._async_sessionmaker() as session:
            result = await session.execute(stmt)
            db_reviews = result.scalars().all()

        if db_reviews:
            return [db_review.to_rmp_review() for db_review in db_reviews]

        # Fall back to JSON files if database is empty
        if not self._instructor_repo:
            return []

        instructor = await self._instructor_repo.get_by_id(instructor_id)
        if not instructor:
            return []

        rmp_data = self._load_rmp_data_from_files()
        reviews = []

        for prof in rmp_data:
            prof_name = prof.get("name", "").strip()
            if prof_name.lower() != instructor.name.lower():
                continue

            prof_reviews = prof.get("reviews", [])
            for review_data in prof_reviews:
                review_date = None
                if review_data.get("date"):
                    try:
                        review_date = datetime.fromisoformat(
                            str(review_data["date"]).replace("Z", "+00:00")
                        )
                    except (ValueError, TypeError):
                        pass

                # Try to match course_id if course code matches
                course_id = None
                course_string = review_data.get("course")
                if course_string and self._course_repo:
                    course_code_match = re.search(
                        r"([A-Z]+)\s*(\d{4})", course_string.upper()
                    )
                    if course_code_match:
                        department = course_code_match.group(1)
                        number = course_code_match.group(2)
                        potential_course_code = f"{department} {number}"
                        db_course = await self._course_repo.get_by_code(
                            potential_course_code
                        )
                        if db_course:
                            course_id = db_course.id

                rmp_review = RmpReview(
                    id=None,
                    instructor_id=instructor_id,
                    course=course_string,
                    course_id=course_id,
                    quality=review_data.get("quality", 0.0),
                    difficulty=review_data.get("difficulty"),
                    comment=review_data.get("comment", ""),
                    would_take_again=review_data.get("would_take_again"),
                    grade=review_data.get("grade"),
                    attendance=review_data.get("attendance"),
                    tags=review_data.get("tags", []) or [],
                    review_date=review_date,
                )
                reviews.append(rmp_review)

        return reviews

    async def get_by_course_id(self, course_id: int) -> list[RmpReview]:
        """Retrieve all RMP reviews for a specific course.
        
        First tries database, then falls back to JSON files if database is empty.
        """
        # Try database first (for backward compatibility)
        stmt = select(DBRmpReview).where(DBRmpReview.course_id == course_id)

        async with self._async_sessionmaker() as session:
            result = await session.execute(stmt)
            db_reviews = result.scalars().all()

        if db_reviews:
            return [db_review.to_rmp_review() for db_review in db_reviews]

        # Fall back to JSON files if database is empty
        if not self._course_repo:
            return []

        course = await self._course_repo.get_by_id(course_id)
        if not course:
            return []

        course_code = f"{course.major_code} {course.course_number}"
        rmp_data = self._load_rmp_data_from_files()
        reviews = []

        for prof in rmp_data:
            prof_reviews = prof.get("reviews", [])
            for review_data in prof_reviews:
                review_course = review_data.get("course")
                if not self._course_code_matches(review_course, course_code):
                    continue

                review_date = None
                if review_data.get("date"):
                    try:
                        review_date = datetime.fromisoformat(
                            str(review_data["date"]).replace("Z", "+00:00")
                        )
                    except (ValueError, TypeError):
                        pass

                # Try to get instructor_id by matching name
                instructor_id = None
                prof_name = prof.get("name", "").strip()
                if self._instructor_repo:
                    instructor = await self._instructor_repo.get_by_name(prof_name)
                    if instructor:
                        instructor_id = instructor.id

                rmp_review = RmpReview(
                    id=None,
                    instructor_id=instructor_id,
                    course=review_course,
                    course_id=course_id,
                    quality=review_data.get("quality", 0.0),
                    difficulty=review_data.get("difficulty"),
                    comment=review_data.get("comment", ""),
                    would_take_again=review_data.get("would_take_again"),
                    grade=review_data.get("grade"),
                    attendance=review_data.get("attendance"),
                    tags=review_data.get("tags", []) or [],
                    review_date=review_date,
                )
                reviews.append(rmp_review)

        return reviews

    async def delete_by_instructor_id(self, instructor_id: int) -> None:
        """Delete all RMP reviews for a specific instructor."""
        delete_stmt = delete(DBRmpReview).where(
            DBRmpReview.instructor_id == instructor_id
        )

        async with self._async_sessionmaker() as session:
            await session.execute(delete_stmt)
            await session.commit()
