import pytest
from unittest.mock import AsyncMock

from app.features.auth.exceptions.authentication import (
    InvalidCredentialsException,
)
from app.features.auth.schemas.authentication import UserLogin
from app.features.auth.services.login import LoginService
from app.features.users.models import User


class TestLogin:

    async def test_login_success(
        self,
        auth_user: User,
    ):
        # Arrange
        db_async_session = AsyncMock()
        user_repo = AsyncMock()
        refresh_token_repo = AsyncMock()
        brute_force_protection = AsyncMock()

        auth_service = LoginService(
            db_async_session=db_async_session,
            user_repo=user_repo,
            refresh_token_repo=refresh_token_repo,
            brute_force_protection=brute_force_protection,
        )

        data = UserLogin(
            email=auth_user.email,
            password="Password123",
        )

        user_repo.get_user_by_email.return_value = auth_user

        # Act
        result = await auth_service.login(
            data=data,
            client_ip="127.0.0.1",
        )

        # Assert
        assert result.access_token
        assert result.refresh_token

        user_repo.get_user_by_email.assert_awaited_once_with(
            data.email,
        )

        refresh_token_repo.create_refresh_token.assert_awaited_once()

        brute_force_protection.reset_attempts.assert_awaited_once_with(
            data.email,
            "127.0.0.1",
        )

        db_async_session.commit.assert_awaited_once()

    async def test_login_user_not_found(self):
        # Arrange
        db_async_session = AsyncMock()
        user_repo = AsyncMock()
        refresh_token_repo = AsyncMock()
        brute_force_protection = AsyncMock()

        auth_service = LoginService(
            db_async_session=db_async_session,
            user_repo=user_repo,
            refresh_token_repo=refresh_token_repo,
            brute_force_protection=brute_force_protection,
        )

        data = UserLogin(
            email="notfound@example.com",
            password="Password123",
        )

        user_repo.get_user_by_email.return_value = None

        # Act / Assert
        with pytest.raises(InvalidCredentialsException):
            await auth_service.login(
                data=data,
                client_ip="127.0.0.1",
            )

        user_repo.get_user_by_email.assert_awaited_once_with(
            data.email,
        )

        refresh_token_repo.create_refresh_token.assert_not_awaited()
        brute_force_protection.record_failed_attempt.assert_not_awaited()
        brute_force_protection.reset_attempts.assert_not_awaited()
        db_async_session.commit.assert_not_awaited()

    async def test_login_wrong_password(
        self,
        auth_user: User,
    ):
        # Arrange
        db_async_session = AsyncMock()
        user_repo = AsyncMock()
        refresh_token_repo = AsyncMock()
        brute_force_protection = AsyncMock()

        auth_service = LoginService(
            db_async_session=db_async_session,
            user_repo=user_repo,
            refresh_token_repo=refresh_token_repo,
            brute_force_protection=brute_force_protection,
        )

        data = UserLogin(
            email=auth_user.email,
            password="WrongPassword123",
        )

        user_repo.get_user_by_email.return_value = auth_user
        brute_force_protection.get_delay.return_value = 0

        # Act / Assert
        with pytest.raises(InvalidCredentialsException):
            await auth_service.login(
                data=data,
                client_ip="127.0.0.1",
            )

        user_repo.get_user_by_email.assert_awaited_once_with(
            data.email,
        )

        brute_force_protection.record_failed_attempt.assert_awaited_once_with(
            data.email,
            "127.0.0.1",
        )

        brute_force_protection.get_delay.assert_awaited_once_with(
            data.email,
            "127.0.0.1",
        )

        brute_force_protection.reset_attempts.assert_not_awaited()
        refresh_token_repo.create_refresh_token.assert_not_awaited()
        db_async_session.commit.assert_not_awaited()
