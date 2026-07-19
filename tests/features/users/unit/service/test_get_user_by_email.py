from app.features.users.models import User
from app.features.users.service import UserService


class TestGetUserByEmail:

    async def test_get_user_by_email_success(
        self,
        user_service: UserService,
        user_repo_mock,
        user: User,
    ):
        # Arrange
        user_repo_mock.get_user_by_email.return_value = user

        # Act
        result = await user_service.get_user_by_email(user.email)

        # Assert
        user_repo_mock.get_user_by_email.assert_awaited_once_with(
            user.email,
        )
        assert result == user

    async def test_get_user_by_email_not_found(
        self,
        user_service: UserService,
        user_repo_mock,
    ):
        # Arrange
        user_repo_mock.get_user_by_email.return_value = None

        # Act
        result = await user_service.get_user_by_email(
            "missing@example.com",
        )

        # Assert
        user_repo_mock.get_user_by_email.assert_awaited_once_with(
            "missing@example.com",
        )
        assert result is None