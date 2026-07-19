from app.features.users.models import User
from app.features.users.repo import UserRepository


class TestGetUserByEmail:

    async def test_success(self, user_repo: UserRepository, created_user_in_db: User):
        # Arrange

        # Act
        user = await user_repo.get_user_by_email(created_user_in_db.email)

        # Assert
        assert user is not None
        assert user.id == created_user_in_db.id
        assert user.email == created_user_in_db.email

    async def test_not_found(self, user_repo: UserRepository):
        # Arrange

        # Act
        user = await user_repo.get_user_by_email("not_found@example.com")

        # Assert
        assert user is None