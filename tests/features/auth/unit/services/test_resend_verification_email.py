from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, Mock

import pytest

from app.features.auth.exceptions.email_verification import (
    EmailAlreadyVerifiedException,
    FailedToCreateVerificationTokenException,
)
from app.features.auth.services.email_verification import (
    EmailVerificationService,
)
from app.features.users.exceptions import UserNotFoundException


class TestResendVerificationEmail:

    async def test_resend_verification_email_success(self):
        # Arrange
        db_async_session = AsyncMock()
        user_repo = AsyncMock()
        verification_token_repo = AsyncMock()
        email_service = AsyncMock()

        service = EmailVerificationService(
            db_async_session=db_async_session,
            user_repo=user_repo,
            verification_token_repo=verification_token_repo,
            email_service=email_service,
        )

        user = Mock()
        user.id = 10
        user.email = "user@example.com"
        user.email_verified = False

        old_token = Mock()
        old_token.id = 1

        user_repo.get_user_by_email.return_value = user
        verification_token_repo.get_verification_token_by_user_id.return_value = (
            old_token
        )

        # Act
        await service.resend_verification_email(user.email)

        # Assert
        user_repo.get_user_by_email.assert_awaited_once_with(
            user.email,
        )

        verification_token_repo.get_verification_token_by_user_id.assert_awaited_once_with(
            user.id,
        )

        verification_token_repo.delete_verification_token_by_id.assert_awaited_once_with(
            old_token.id,
        )

        verification_token_repo.create_verification_token.assert_awaited_once()

        db_async_session.commit.assert_awaited_once()

        email_service.send_verification_email.assert_awaited_once()

    async def test_resend_verification_email_user_not_found(self):
        # Arrange
        db_async_session = AsyncMock()
        user_repo = AsyncMock()
        verification_token_repo = AsyncMock()
        email_service = AsyncMock()

        service = EmailVerificationService(
            db_async_session=db_async_session,
            user_repo=user_repo,
            verification_token_repo=verification_token_repo,
            email_service=email_service,
        )

        user_repo.get_user_by_email.return_value = None

        # Act / Assert
        with pytest.raises(UserNotFoundException):
            await service.resend_verification_email(
                "notfound@example.com",
            )

        user_repo.get_user_by_email.assert_awaited_once_with(
            "notfound@example.com",
        )

        verification_token_repo.create_verification_token.assert_not_awaited()
        db_async_session.commit.assert_not_awaited()
        email_service.send_verification_email.assert_not_awaited()

    async def test_resend_verification_email_already_verified(self):
        # Arrange
        db_async_session = AsyncMock()
        user_repo = AsyncMock()
        verification_token_repo = AsyncMock()
        email_service = AsyncMock()

        service = EmailVerificationService(
            db_async_session=db_async_session,
            user_repo=user_repo,
            verification_token_repo=verification_token_repo,
            email_service=email_service,
        )

        user = Mock()
        user.id = 10
        user.email = "verified@example.com"
        user.email_verified = True

        user_repo.get_user_by_email.return_value = user

        # Act / Assert
        with pytest.raises(EmailAlreadyVerifiedException):
            await service.resend_verification_email(
                user.email,
            )

        verification_token_repo.get_verification_token_by_user_id.assert_not_awaited()
        verification_token_repo.create_verification_token.assert_not_awaited()
        db_async_session.commit.assert_not_awaited()
        email_service.send_verification_email.assert_not_awaited()

    async def test_resend_verification_email_deletes_old_token(self):
        # Arrange
        db_async_session = AsyncMock()
        user_repo = AsyncMock()
        verification_token_repo = AsyncMock()
        email_service = AsyncMock()

        service = EmailVerificationService(
            db_async_session=db_async_session,
            user_repo=user_repo,
            verification_token_repo=verification_token_repo,
            email_service=email_service,
        )

        user = Mock()
        user.id = 10
        user.email = "user@example.com"
        user.email_verified = False

        old_token = Mock()
        old_token.id = 5

        user_repo.get_user_by_email.return_value = user
        verification_token_repo.get_verification_token_by_user_id.return_value = (
            old_token
        )

        # Act
        await service.resend_verification_email(user.email)

        # Assert
        verification_token_repo.delete_verification_token_by_id.assert_awaited_once_with(
            old_token.id,
        )

    async def test_resend_verification_email_without_old_token(self):
        # Arrange
        db_async_session = AsyncMock()
        user_repo = AsyncMock()
        verification_token_repo = AsyncMock()
        email_service = AsyncMock()

        service = EmailVerificationService(
            db_async_session=db_async_session,
            user_repo=user_repo,
            verification_token_repo=verification_token_repo,
            email_service=email_service,
        )

        user = Mock()
        user.id = 10
        user.email = "user@example.com"
        user.email_verified = False

        user_repo.get_user_by_email.return_value = user
        verification_token_repo.get_verification_token_by_user_id.return_value = (
            None
        )

        # Act
        await service.resend_verification_email(user.email)

        # Assert
        verification_token_repo.delete_verification_token_by_id.assert_not_awaited()
        verification_token_repo.create_verification_token.assert_awaited_once()

    async def test_resend_verification_email_failed_to_create_token(
        self,
        monkeypatch,
    ):
        # Arrange
        db_async_session = AsyncMock()
        user_repo = AsyncMock()
        verification_token_repo = AsyncMock()
        email_service = AsyncMock()

        service = EmailVerificationService(
            db_async_session=db_async_session,
            user_repo=user_repo,
            verification_token_repo=verification_token_repo,
            email_service=email_service,
        )

        user = Mock()
        user.id = 10
        user.email = "user@example.com"
        user.email_verified = False

        user_repo.get_user_by_email.return_value = user
        verification_token_repo.get_verification_token_by_user_id.return_value = (
            None
        )

        monkeypatch.setattr(
            "app.features.auth.services.email_verification."
            "create_email_verification_token",
            lambda: None,
        )

        # Act / Assert
        with pytest.raises(FailedToCreateVerificationTokenException):
            await service.resend_verification_email(user.email)

        verification_token_repo.create_verification_token.assert_not_awaited()
        db_async_session.commit.assert_not_awaited()
        email_service.send_verification_email.assert_not_awaited()

    async def test_resend_verification_email_creates_new_token(
        self,
    ):
        # Arrange
        db_async_session = AsyncMock()
        user_repo = AsyncMock()
        verification_token_repo = AsyncMock()
        email_service = AsyncMock()

        service = EmailVerificationService(
            db_async_session=db_async_session,
            user_repo=user_repo,
            verification_token_repo=verification_token_repo,
            email_service=email_service,
        )

        user = Mock()
        user.id = 10
        user.email = "user@example.com"
        user.email_verified = False

        user_repo.get_user_by_email.return_value = user
        verification_token_repo.get_verification_token_by_user_id.return_value = None

        # Act
        await service.resend_verification_email(user.email)

        # Assert
        token_data = (
            verification_token_repo.create_verification_token
            .await_args.args[0]
        )

        assert token_data["token"]
        assert token_data["user_id"] == user.id
        assert token_data["expires_at"] is not None

    async def test_resend_verification_email_sends_email(self):
        # Arrange
        db_async_session = AsyncMock()
        user_repo = AsyncMock()
        verification_token_repo = AsyncMock()
        email_service = AsyncMock()

        service = EmailVerificationService(
            db_async_session=db_async_session,
            user_repo=user_repo,
            verification_token_repo=verification_token_repo,
            email_service=email_service,
        )

        user = Mock()
        user.id = 10
        user.email = "user@example.com"
        user.email_verified = False

        user_repo.get_user_by_email.return_value = user
        verification_token_repo.get_verification_token_by_user_id.return_value = None

        # Act
        await service.resend_verification_email(user.email)

        # Assert
        email_service.send_verification_email.assert_awaited_once()

        email_data = (
            email_service.send_verification_email
            .await_args.kwargs
        )

        assert email_data["recipient"] == user.email
        assert email_data["token"]

    async def test_resend_verification_email_token_expires_in_24_hours(
        self,
    ):
        # Arrange
        db_async_session = AsyncMock()
        user_repo = AsyncMock()
        verification_token_repo = AsyncMock()
        email_service = AsyncMock()

        service = EmailVerificationService(
            db_async_session=db_async_session,
            user_repo=user_repo,
            verification_token_repo=verification_token_repo,
            email_service=email_service,
        )

        user = Mock()
        user.id = 10
        user.email = "user@example.com"
        user.email_verified = False

        user_repo.get_user_by_email.return_value = user
        verification_token_repo.get_verification_token_by_user_id.return_value = None

        before = datetime.now(timezone.utc)

        # Act
        await service.resend_verification_email(user.email)

        after = datetime.now(timezone.utc)

        # Assert
        token_data = (
            verification_token_repo.create_verification_token
            .await_args.args[0]
        )

        expires_at = token_data["expires_at"]

        assert (
            before + timedelta(hours=24)
            <= expires_at
            <= after + timedelta(hours=24)
        )
