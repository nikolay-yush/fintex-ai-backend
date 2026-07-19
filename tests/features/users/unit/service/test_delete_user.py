from app.features.users.models import User
from app.features.users.service import UserService
from unittest.mock import AsyncMock

class TestDeleteUser:

    async def test_delete_user_success(
        self,
        user_service: UserService,
        user_repo_mock: AsyncMock,
        user: User,
    ):
        # Arrange
        user_repo_mock.delete_one.return_value = user

        # Act
        result = await user_service.delete_user(user)

        # Assert
        user_repo_mock.delete_one.assert_awaited_once_with(
            user.id,
        )
        assert result == user

    async def test_delete_user_not_found(
        self,
        user_service: UserService,
        user_repo_mock: AsyncMock,
        user: User,
    ):
        # Arrange
        user_repo_mock.delete_one.return_value = None

        # Act
        result = await user_service.delete_user(user)

        # Assert
        user_repo_mock.delete_one.assert_awaited_once_with(
            user.id,
        )
        assert result is None