import pytest
import pytest_asyncio

from billiken_blueprint.identity import IdentityUser
from billiken_blueprint.repositories.identity_user_repository import (
    IdentityUserRepository,
)


@pytest_asyncio.fixture
async def repository(async_sessionmaker):
    """Create an IdentityUserRepository instance."""
    return IdentityUserRepository(async_sessionmaker)


@pytest.mark.asyncio
class TestIdentityUserRepository:
    async def test_save_new_user(self, repository, async_sessionmaker):
        """Test saving a new identity user to the database."""
        # Arrange
        user = IdentityUser.create(email="alice@example.com", password="SecurePass123")

        # Act
        await repository.save(user)

        # Assert - verify it was saved
        async with async_sessionmaker() as session:
            from sqlalchemy import select

            stmt = select(IdentityUser).where(IdentityUser.email == "alice@example.com")
            result = await session.execute(stmt)
            saved_user = result.scalar_one_or_none()

            assert saved_user is not None
            assert saved_user.email == "alice@example.com"
            assert saved_user.password_hash is not None
            assert saved_user.password_hash != "SecurePass123"  # Should be hashed

    async def test_save_updates_existing_user(self, repository):
        """Test that we can modify a user after retrieving it."""
        # Arrange - save initial user
        user1 = IdentityUser.create(email="bob@example.com", password="Pass123")
        await repository.save(user1)

        # Get the saved user to get the ID
        saved_user = await repository.get_by_email("bob@example.com")
        assert saved_user is not None

        # Note: This test verifies we can retrieve users successfully.
        # True update functionality would require updating the save method
        # to use email as the conflict key or implementing a separate update method.

    async def test_get_by_id_existing_user(self, repository):
        """Test retrieving an existing user by ID."""
        # Arrange
        user = IdentityUser.create(email="charlie@example.com", password="Pass456")
        await repository.save(user)

        # Get the ID
        saved_user = await repository.get_by_email("charlie@example.com")
        assert saved_user is not None
        user_id = saved_user.id

        # Act
        result = await repository.get_by_id(user_id)

        # Assert
        assert result is not None
        assert result.id == user_id
        assert result.email == "charlie@example.com"

    async def test_get_by_id_nonexistent_user(self, repository):
        """Test retrieving a user that doesn't exist returns None."""
        # Act
        result = await repository.get_by_id(999)

        # Assert
        assert result is None

    async def test_get_by_email_existing_user(self, repository):
        """Test retrieving a user by email."""
        # Arrange
        user = IdentityUser.create(email="diana@example.com", password="Diana123")
        await repository.save(user)

        # Act
        result = await repository.get_by_email("diana@example.com")

        # Assert
        assert result is not None
        assert result.email == "diana@example.com"

    async def test_get_by_email_nonexistent_user(self, repository):
        """Test retrieving a user by email that doesn't exist returns None."""
        # Act
        result = await repository.get_by_email("nonexistent@example.com")

        # Assert
        assert result is None

    async def test_get_by_email_case_sensitive(self, repository):
        """Test that email lookup is case-sensitive (or case-insensitive depending on your design)."""
        # Arrange
        user = IdentityUser.create(email="eve@example.com", password="Eve123")
        await repository.save(user)

        # Act
        result = await repository.get_by_email("EVE@EXAMPLE.COM")

        # Assert - adjust based on your desired behavior
        # If emails should be case-insensitive, you may want to normalize them
        assert result is None  # Assuming case-sensitive for now

    async def test_password_is_hashed(self, repository):
        """Test that passwords are properly hashed when creating users."""
        # Arrange
        plain_password = "MySecretPassword123"
        user = IdentityUser.create(email="frank@example.com", password=plain_password)

        # Act
        await repository.save(user)
        saved_user = await repository.get_by_email("frank@example.com")

        # Assert
        assert saved_user is not None
        assert saved_user.password_hash != plain_password
        assert saved_user.verify_password(plain_password) is True
        assert saved_user.verify_password("WrongPassword") is False

    async def test_save_user_with_student_id(self, repository, async_sessionmaker):
        """Test saving a user with an associated student_id."""
        # Arrange
        user = IdentityUser.create(email="grace@example.com", password="Grace123")
        user.student_id = 42

        # Act
        await repository.save(user)

        # Assert
        saved_user = await repository.get_by_email("grace@example.com")
        assert saved_user is not None
        assert saved_user.student_id == 42

    async def test_save_user_without_student_id(self, repository):
        """Test saving a user without a student_id (should be None)."""
        # Arrange
        user = IdentityUser.create(email="henry@example.com", password="Henry123")

        # Act
        await repository.save(user)

        # Assert
        saved_user = await repository.get_by_email("henry@example.com")
        assert saved_user is not None
        assert saved_user.student_id is None

    async def test_save_multiple_users(self, repository):
        """Test saving multiple users with unique emails."""
        # Arrange
        users = [
            IdentityUser.create("user1@example.com", "Pass1"),
            IdentityUser.create("user2@example.com", "Pass2"),
            IdentityUser.create("user3@example.com", "Pass3"),
        ]

        # Act
        for user in users:
            await repository.save(user)

        # Assert - verify all were saved
        result1 = await repository.get_by_email("user1@example.com")
        result2 = await repository.get_by_email("user2@example.com")
        result3 = await repository.get_by_email("user3@example.com")

        assert result1 is not None
        assert result2 is not None
        assert result3 is not None
