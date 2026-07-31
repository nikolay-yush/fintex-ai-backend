import pytest
from unittest.mock import AsyncMock

from app.features.auth.exceptions import (
    EmailVerificationTokenExpiredException,
    EmailVerificationTokenNotFoundException,
)
from app.features.auth.models import EmailVerificationToken
from app.features.auth.service import AuthService
from app.features.users.models import User


class TestVerifyEmail:

    async def test_verify_email_success(
        self,
        user: User,
    ):
        # Arrange
        auth_repo = AsyncMock()
        user_repo = AsyncMock()
        db_async_session = AsyncMock()

        auth_service = AuthService(
            db_async_session=db_async_session,
            auth_repo=auth_repo,
            user_repo=user_repo,
        )

        verification_token = EmailVerificationToken(
            id=1,
            token="token",
            user_id=user.id,
            expires_at=user.created_at,
        )

        verification_token.expires_at = (
            verification_token.expires_at.replace(
                year=verification_token.expires_at.year + 1
            )
        )

        auth_repo.get_verification_token.return_value = (
            verification_token
        )

        user_repo.get_one_by_id.return_value = user

        # Act
        await auth_service.verify_email("token")

        # Assert
        assert user.email_verified is True

        auth_repo.delete_one.assert_awaited_once_with(
            verification_token.id,
        )

        db_async_session.commit.assert_awaited_once()

    async def test_verify_email_token_not_found(
        self,
    ):
        # Arrange
        auth_repo = AsyncMock()
        user_repo = AsyncMock()
        db_async_session = AsyncMock()

        auth_service = AuthService(
            db_async_session=db_async_session,
            auth_repo=auth_repo,
            user_repo=user_repo,
        )

        auth_repo.get_verification_token.return_value = None

        # Act / Assert
        with pytest.raises(
            EmailVerificationTokenNotFoundException,
        ):
            await auth_service.verify_email("token")

    async def test_verify_email_expired(
        self,
        user: User,
    ):
        # Arrange
        auth_repo = AsyncMock()
        user_repo = AsyncMock()
        db_async_session = AsyncMock()

        auth_service = AuthService(
            db_async_session=db_async_session,
            auth_repo=auth_repo,
            user_repo=user_repo,
        )

        verification_token = EmailVerificationToken(
            id=1,
            token="token",
            user_id=user.id,
            expires_at=user.created_at,
        )

        auth_repo.get_verification_token.return_value = (
            verification_token
        )

        # Act / Assert
        with pytest.raises(
            EmailVerificationTokenExpiredException,
        ):
            await auth_service.verify_email("token")