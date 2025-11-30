import pytest
from datetime import datetime
from billiken_blueprint.repositories.rating_repository import RatingRepository
from billiken_blueprint.domain.ratings.rating import Rating


@pytest.mark.asyncio
class TestRatingRepository:
    """Test suite for RatingRepository."""

    async def test_save_new_rating(self, rating_repository: RatingRepository):
        """Test saving a new rating to the database."""
        rating = Rating(
            id=None,
            course_id=1,
            professor_id=2,
            student_id=100,
            rating_value=5,
            description="Excellent professor!",
            created_at=None,
            difficulty=3.5,
            would_take_again=True,
            grade="A",
            attendance="Mandatory",
        )

        saved = await rating_repository.save(rating)

        assert saved.id is not None
        assert saved.rating_value == 5
        assert saved.description == "Excellent professor!"
        assert saved.created_at is not None  # Should be set automatically

    async def test_save_and_update_rating(self, rating_repository: RatingRepository):
        """Test saving and then updating a rating."""
        # Create and save a new rating
        rating = Rating(
            id=None,
            course_id=1,
            professor_id=2,
            student_id=101,
            rating_value=3,
            description="Average class",
            created_at=None,
            difficulty=2.5,
            would_take_again=False,
            grade="B",
            attendance="Recommended",
        )
        saved = await rating_repository.save(rating)
        rating_id = saved.id
        original_created_at = saved.created_at

        # Update the rating
        updated_rating = Rating(
            id=rating_id,
            course_id=1,
            professor_id=2,
            student_id=101,
            rating_value=4,
            description="Updated: Better than expected",
            created_at=original_created_at,
            difficulty=2.0,
            would_take_again=True,
            grade="A-",
            attendance="Mandatory",
        )
        result = await rating_repository.save(updated_rating)

        assert result.id == rating_id
        assert result.rating_value == 4
        assert result.description == "Updated: Better than expected"

    async def test_get_all_empty(self, rating_repository: RatingRepository):
        """Test getting all ratings when database is empty."""
        ratings = await rating_repository.get_all()
        assert ratings == []

    async def test_get_all_multiple_ratings(self, rating_repository: RatingRepository):
        """Test retrieving all ratings when multiple exist."""
        # Save multiple ratings
        rating1 = Rating(
            id=None,
            course_id=1,
            professor_id=1,
            student_id=200,
            rating_value=5,
            description="Great!",
            difficulty=2.0,
            would_take_again=True,
            grade="A",
            attendance="Mandatory",
        )
        rating2 = Rating(
            id=None,
            course_id=2,
            professor_id=2,
            student_id=201,
            rating_value=3,
            description="Okay",
            difficulty=3.0,
            would_take_again=False,
            grade="C",
            attendance="Not taken",
        )
        rating3 = Rating(
            id=None,
            course_id=1,
            professor_id=2,
            student_id=202,
            rating_value=4,
            description="Good",
            difficulty=2.5,
            would_take_again=True,
            grade="B+",
            attendance="Recommended",
        )

        await rating_repository.save(rating1)
        await rating_repository.save(rating2)
        await rating_repository.save(rating3)

        # Get all ratings
        all_ratings = await rating_repository.get_all()

        assert len(all_ratings) == 3
        assert all(isinstance(r, Rating) for r in all_ratings)

    async def test_get_all_filtered_by_instructor(
        self, rating_repository: RatingRepository
    ):
        """Test retrieving ratings filtered by instructor ID."""
        # Save ratings for different instructors
        rating1 = Rating(
            id=None,
            course_id=1,
            professor_id=10,
            student_id=300,
            rating_value=5,
            description="Amazing!",
            difficulty=1.5,
            would_take_again=True,
            grade="A",
            attendance="Mandatory",
        )
        rating2 = Rating(
            id=None,
            course_id=2,
            professor_id=10,
            student_id=301,
            rating_value=4,
            description="Good",
            difficulty=2.0,
            would_take_again=True,
            grade="A",
            attendance="Mandatory",
        )
        rating3 = Rating(
            id=None,
            course_id=1,
            professor_id=20,
            student_id=302,
            rating_value=2,
            description="Not great",
            difficulty=4.0,
            would_take_again=False,
            grade="D",
            attendance="Not taken",
        )

        await rating_repository.save(rating1)
        await rating_repository.save(rating2)
        await rating_repository.save(rating3)

        # Get ratings for instructor 10
        instructor_10_ratings = await rating_repository.get_all(instructor_id=10)
        assert len(instructor_10_ratings) == 2

        # Get ratings for instructor 20
        instructor_20_ratings = await rating_repository.get_all(instructor_id=20)
        assert len(instructor_20_ratings) == 1

    async def test_get_all_filtered_by_course(
        self, rating_repository: RatingRepository
    ):
        """Test retrieving ratings filtered by course ID."""
        # Save ratings for different courses
        rating1 = Rating(
            id=None,
            course_id=100,
            professor_id=1,
            student_id=400,
            rating_value=5,
            description="Course was great!",
            difficulty=2.0,
            would_take_again=True,
            grade="A",
            attendance="Mandatory",
        )
        rating2 = Rating(
            id=None,
            course_id=100,
            professor_id=2,
            student_id=401,
            rating_value=4,
            description="Good course",
            difficulty=2.5,
            would_take_again=True,
            grade="A",
            attendance="Mandatory",
        )
        rating3 = Rating(
            id=None,
            course_id=200,
            professor_id=3,
            student_id=402,
            rating_value=3,
            description="Okay course",
            difficulty=3.0,
            would_take_again=False,
            grade="B",
            attendance="Recommended",
        )

        await rating_repository.save(rating1)
        await rating_repository.save(rating2)
        await rating_repository.save(rating3)

        # Get ratings for course 100
        course_100_ratings = await rating_repository.get_all(course_id=100)
        assert len(course_100_ratings) == 2

        # Get ratings for course 200
        course_200_ratings = await rating_repository.get_all(course_id=200)
        assert len(course_200_ratings) == 1

    async def test_get_all_filtered_by_both_instructor_and_course(
        self, rating_repository: RatingRepository
    ):
        """Test retrieving ratings filtered by both instructor and course ID."""
        # Save multiple ratings
        rating1 = Rating(
            id=None,
            course_id=50,
            professor_id=5,
            student_id=500,
            rating_value=5,
            description="Perfect!",
            difficulty=1.0,
            would_take_again=True,
            grade="A",
            attendance="Mandatory",
        )
        rating2 = Rating(
            id=None,
            course_id=50,
            professor_id=6,
            student_id=501,
            rating_value=3,
            description="Meh",
            difficulty=3.5,
            would_take_again=False,
            grade="C",
            attendance="Not taken",
        )
        rating3 = Rating(
            id=None,
            course_id=60,
            professor_id=5,
            student_id=502,
            rating_value=2,
            description="Not good",
            difficulty=4.0,
            would_take_again=False,
            grade="D",
            attendance="Not taken",
        )

        await rating_repository.save(rating1)
        await rating_repository.save(rating2)
        await rating_repository.save(rating3)

        # Get ratings for course 50 and instructor 5
        filtered = await rating_repository.get_all(course_id=50, instructor_id=5)
        assert len(filtered) == 1
        assert filtered[0].rating_value == 5

    async def test_delete_rating(self, rating_repository: RatingRepository):
        """Test deleting a rating."""
        # Save a rating
        rating = Rating(
            id=None,
            course_id=1,
            professor_id=1,
            student_id=600,
            rating_value=4,
            description="To be deleted",
            difficulty=2.0,
            would_take_again=True,
            grade="A",
            attendance="Mandatory",
        )
        saved = await rating_repository.save(rating)
        assert saved.id is not None
        rating_id = saved.id

        # Delete the rating
        await rating_repository.delete(rating_id)

        # Verify it's gone
        all_ratings = await rating_repository.get_all()
        assert len(all_ratings) == 0

    async def test_save_rating_with_minimal_fields(
        self, rating_repository: RatingRepository
    ):
        """Test saving a rating with only required fields."""
        rating = Rating(
            id=None,
            course_id=None,
            professor_id=None,
            student_id=700,
            rating_value=3,
            description="Minimal rating",
        )

        saved = await rating_repository.save(rating)

        assert saved.id is not None
        assert saved.student_id == 700
        assert saved.rating_value == 3
        assert saved.created_at is not None
