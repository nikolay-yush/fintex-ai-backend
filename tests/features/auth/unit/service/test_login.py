import pytest
from unittest.mock import AsyncMock

from app.features.auth.exceptions import InvalidCredentialsException
from app.features.auth.schemas import UserLogin
from app.features.auth.service import AuthService
from app.features.users.models import User
from tests.features.auth.conftest import user


class TestLogin:

    async def test_login_success(
        self,
        auth_user: User
    ):
        # Arrange
        user_repo = AsyncMock()
        auth_service = AuthService(
            user_repo=user_repo,
        )

        data = UserLogin(
            email=auth_user.email,
            password="Password123",
        )

        user_repo.get_user_by_email.return_value = auth_user

        # Act
        result = await auth_service.login(data)

        # Assert
        assert result.access_token
        assert result.token_type == "bearer"

        user_repo.get_user_by_email.assert_awaited_once_with(
            data.email,
        )

    async def test_login_user_not_found(self):
        # Arrange
        user_repo = AsyncMock()
        auth_service = AuthService(
            user_repo=user_repo,
        )

        data = UserLogin(
            email="notfound@example.com",
            password="Password123",
        )

        user_repo.get_user_by_email.return_value = None

        # Act / Assert
        with pytest.raises(InvalidCredentialsException):
            await auth_service.login(data)

        user_repo.get_user_by_email.assert_awaited_once_with(
            data.email,
        )

    async def test_login_wrong_password(
        self,
        auth_user: User,
    ):
        # Arrange
        user_repo = AsyncMock()
        auth_service = AuthService(
            user_repo=user_repo,
        )

        data = UserLogin(
            email=auth_user.email,
            password="WrongPassword123",
        )

        user_repo.get_user_by_email.return_value = auth_user

        # Act / Assert
        with pytest.raises(InvalidCredentialsException):
            await auth_service.login(data)

        user_repo.get_user_by_email.assert_awaited_once_with(
            data.email,
        )