import pytest
from datetime import datetime
from billiken_blueprint.repositories.rmp_review_repository import RmpReviewRepository
from billiken_blueprint.domain.ratings.rmp_review import RmpReview


@pytest.mark.asyncio
class TestRmpReviewRepository:
    """Test suite for RmpReviewRepository."""

    async def test_save_new_review(self, rmp_review_repository: RmpReviewRepository):
        """Test saving a new RMP review to the database."""
        review = RmpReview(
            id=None,
            instructor_id=1,
            course="CSCI 1000",
            course_id=100,
            quality=4.5,
            difficulty=2.5,
            comment="Great professor!",
            would_take_again=True,
            grade="A",
            attendance="Mandatory",
            tags=["helpful", "organized"],
            review_date=datetime(2024, 1, 15),
        )

        saved = await rmp_review_repository.save(review)

        assert saved.id is not None
        assert saved.instructor_id == 1
        assert saved.quality == 4.5
        assert "helpful" in saved.tags

    async def test_save_and_update_review(
        self, rmp_review_repository: RmpReviewRepository
    ):
        """Test saving and then updating a review."""
        # Create and save a new review
        review = RmpReview(
            id=None,
            instructor_id=2,
            course="MATH 1500",
            course_id=200,
            quality=3.0,
            difficulty=4.0,
            comment="Challenging but fair",
            would_take_again=False,
            grade="B",
            attendance="Recommended",
            tags=["strict"],
            review_date=datetime(2024, 1, 10),
        )
        saved = await rmp_review_repository.save(review)
        review_id = saved.id

        # Update the review
        updated_review = RmpReview(
            id=review_id,
            instructor_id=2,
            course="MATH 1500",
            course_id=200,
            quality=3.5,
            difficulty=3.5,
            comment="Updated: Better than expected",
            would_take_again=True,
            grade="A-",
            attendance="Mandatory",
            tags=["strict", "fair"],
            review_date=datetime(2024, 1, 10),
        )
        result = await rmp_review_repository.save(updated_review)

        assert result.id == review_id
        assert result.quality == 3.5

    async def test_save_many_reviews(self, rmp_review_repository: RmpReviewRepository):
        """Test saving multiple reviews in one transaction."""
        reviews = [
            RmpReview(
                id=None,
                instructor_id=3,
                course="PHYS 2000",
                course_id=300,
                quality=5.0,
                difficulty=3.0,
                comment="Amazing!",
                would_take_again=True,
                grade="A",
                attendance="Mandatory",
                tags=["excellent"],
                review_date=datetime(2024, 2, 1),
            ),
            RmpReview(
                id=None,
                instructor_id=3,
                course="PHYS 2001",
                course_id=301,
                quality=4.8,
                difficulty=2.8,
                comment="Very good",
                would_take_again=True,
                grade="A",
                attendance="Mandatory",
                tags=["excellent", "clear"],
                review_date=datetime(2024, 2, 5),
            ),
            RmpReview(
                id=None,
                instructor_id=4,
                course="CHEM 1000",
                course_id=400,
                quality=3.2,
                difficulty=3.5,
                comment="Okay",
                would_take_again=False,
                grade="C",
                attendance="Not taken",
                tags=["average"],
                review_date=datetime(2024, 2, 10),
            ),
        ]

        await rmp_review_repository.save_many(reviews)

        # Verify by retrieving all reviews for instructor 3
        instructor_3_reviews = await rmp_review_repository.get_by_instructor_id(3)
        assert len(instructor_3_reviews) == 2

    async def test_get_by_instructor_id(
        self, rmp_review_repository: RmpReviewRepository
    ):
        """Test retrieving reviews by instructor ID."""
        # Save reviews for different instructors
        review1 = RmpReview(
            id=None,
            instructor_id=10,
            course="CSCI 1000",
            course_id=1000,
            quality=4.5,
            difficulty=2.0,
            comment="Good",
            would_take_again=True,
            grade="A",
            attendance="Mandatory",
            tags=["helpful"],
            review_date=datetime(2024, 3, 1),
        )
        review2 = RmpReview(
            id=None,
            instructor_id=10,
            course="CSCI 2000",
            course_id=2000,
            quality=4.0,
            difficulty=3.0,
            comment="Decent",
            would_take_again=True,
            grade="A",
            attendance="Mandatory",
            tags=["fair"],
            review_date=datetime(2024, 3, 5),
        )
        review3 = RmpReview(
            id=None,
            instructor_id=20,
            course="MATH 1500",
            course_id=1500,
            quality=2.5,
            difficulty=4.5,
            comment="Hard",
            would_take_again=False,
            grade="D",
            attendance="Not taken",
            tags=["difficult"],
            review_date=datetime(2024, 3, 10),
        )

        await rmp_review_repository.save(review1)
        await rmp_review_repository.save(review2)
        await rmp_review_repository.save(review3)

        # Get reviews for instructor 10
        inst_10_reviews = await rmp_review_repository.get_by_instructor_id(10)
        assert len(inst_10_reviews) == 2

        # Get reviews for instructor 20
        inst_20_reviews = await rmp_review_repository.get_by_instructor_id(20)
        assert len(inst_20_reviews) == 1

    async def test_get_by_course_id(self, rmp_review_repository: RmpReviewRepository):
        """Test retrieving reviews by course ID."""
        # Save reviews for different courses
        review1 = RmpReview(
            id=None,
            instructor_id=5,
            course="CSCI 1000",
            course_id=5000,
            quality=4.0,
            difficulty=2.5,
            comment="Good course",
            would_take_again=True,
            grade="A",
            attendance="Mandatory",
            tags=["good"],
            review_date=datetime(2024, 4, 1),
        )
        review2 = RmpReview(
            id=None,
            instructor_id=6,
            course="CSCI 1000",
            course_id=5000,
            quality=3.8,
            difficulty=2.8,
            comment="Pretty good",
            would_take_again=True,
            grade="A",
            attendance="Mandatory",
            tags=["solid"],
            review_date=datetime(2024, 4, 5),
        )
        review3 = RmpReview(
            id=None,
            instructor_id=7,
            course="MATH 2000",
            course_id=6000,
            quality=3.0,
            difficulty=4.0,
            comment="Challenging",
            would_take_again=False,
            grade="B",
            attendance="Recommended",
            tags=["hard"],
            review_date=datetime(2024, 4, 10),
        )

        await rmp_review_repository.save(review1)
        await rmp_review_repository.save(review2)
        await rmp_review_repository.save(review3)

        # Get reviews for course 5000
        course_5000_reviews = await rmp_review_repository.get_by_course_id(5000)
        assert len(course_5000_reviews) == 2

        # Get reviews for course 6000
        course_6000_reviews = await rmp_review_repository.get_by_course_id(6000)
        assert len(course_6000_reviews) == 1

    async def test_delete_by_instructor_id(
        self, rmp_review_repository: RmpReviewRepository
    ):
        """Test deleting all reviews for an instructor."""
        # Save reviews for an instructor
        review1 = RmpReview(
            id=None,
            instructor_id=50,
            course="CSCI 1000",
            course_id=5001,
            quality=4.5,
            difficulty=2.0,
            comment="Excellent",
            would_take_again=True,
            grade="A",
            attendance="Mandatory",
            tags=["best"],
            review_date=datetime(2024, 5, 1),
        )
        review2 = RmpReview(
            id=None,
            instructor_id=50,
            course="CSCI 2000",
            course_id=5002,
            quality=4.3,
            difficulty=2.5,
            comment="Great",
            would_take_again=True,
            grade="A",
            attendance="Mandatory",
            tags=["good"],
            review_date=datetime(2024, 5, 5),
        )

        await rmp_review_repository.save(review1)
        await rmp_review_repository.save(review2)

        # Verify reviews exist
        reviews_before = await rmp_review_repository.get_by_instructor_id(50)
        assert len(reviews_before) == 2

        # Delete all reviews for instructor 50
        await rmp_review_repository.delete_by_instructor_id(50)

        # Verify reviews are deleted
        reviews_after = await rmp_review_repository.get_by_instructor_id(50)
        assert len(reviews_after) == 0

    async def test_save_review_with_empty_tags(
        self, rmp_review_repository: RmpReviewRepository
    ):
        """Test saving a review with empty tags list."""
        review = RmpReview(
            id=None,
            instructor_id=8,
            course="PHYS 1000",
            course_id=8000,
            quality=3.5,
            difficulty=3.5,
            comment="No tags",
            would_take_again=False,
            grade="C",
            attendance="Not taken",
            tags=[],
            review_date=datetime(2024, 6, 1),
        )

        saved = await rmp_review_repository.save(review)

        assert saved.id is not None
        assert saved.tags == []

    async def test_save_review_without_course_id(
        self, rmp_review_repository: RmpReviewRepository
    ):
        """Test saving a review without a course ID."""
        review = RmpReview(
            id=None,
            instructor_id=9,
            course="UNKNOWN COURSE",
            course_id=None,
            quality=2.5,
            difficulty=3.5,
            comment="Unknown course",
            would_take_again=False,
            grade="D",
            attendance="Not taken",
            tags=["unknown"],
            review_date=datetime(2024, 7, 1),
        )

        saved = await rmp_review_repository.save(review)

        assert saved.id is not None
        assert saved.course_id is None
