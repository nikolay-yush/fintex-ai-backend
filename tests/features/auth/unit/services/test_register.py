from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest

from app.features.auth.exceptions.email_verification import (
    FailedToCreateVerificationTokenException,
)
from app.features.auth.exceptions.registration import (
    FailedToCreateUserException,
    UserAlreadyExistsException,
)
from app.features.auth.schemas.registration import UserRegister
from app.features.auth.services.registration import RegistrationService


class TestRegistration:

    async def test_register_success(self):
        # Arrange
        db_async_session = AsyncMock()
        user_repo = AsyncMock()
        verification_token_repo = AsyncMock()
        email_service = AsyncMock()

        auth_service = RegistrationService(
            db_async_session=db_async_session,
            user_repo=user_repo,
            verification_token_repo=verification_token_repo,
            email_service=email_service,
        )

        data = UserRegister(
            email="new@example.com",
            full_name="New User",
            password="Password123",
        )

        user = AsyncMock()
        user.id = 1
        user.email = data.email

        user_repo.get_user_by_email.return_value = None
        user_repo.create_one.return_value = user
        verification_token_repo.create_one.return_value = None
        email_service.send_verification_email.return_value = None

        # Act
        result = await auth_service.register(data)

        # Assert
        assert result == user

        user_repo.get_user_by_email.assert_awaited_once_with(
            data.email,
        )

        user_repo.create_one.assert_awaited_once()

        verification_token_repo.create_one.assert_awaited_once()

        db_async_session.commit.assert_awaited_once()

        email_service.send_verification_email.assert_awaited_once()

    async def test_register_user_already_exists(self):
        # Arrange
        db_async_session = AsyncMock()
        user_repo = AsyncMock()
        verification_token_repo = AsyncMock()
        email_service = AsyncMock()

        auth_service = RegistrationService(
            db_async_session=db_async_session,
            user_repo=user_repo,
            verification_token_repo=verification_token_repo,
            email_service=email_service,
        )

        data = UserRegister(
            email="existing@example.com",
            full_name="Existing User",
            password="Password123",
        )

        user_repo.get_user_by_email.return_value = AsyncMock()

        # Act / Assert
        with pytest.raises(UserAlreadyExistsException):
            await auth_service.register(data)

        user_repo.get_user_by_email.assert_awaited_once_with(
            data.email,
        )

        user_repo.create_one.assert_not_awaited()
        verification_token_repo.create_one.assert_not_awaited()
        db_async_session.commit.assert_not_awaited()
        email_service.send_verification_email.assert_not_awaited()

    async def test_register_failed_to_create_user(self):
        # Arrange
        db_async_session = AsyncMock()
        user_repo = AsyncMock()
        verification_token_repo = AsyncMock()
        email_service = AsyncMock()

        auth_service = RegistrationService(
            db_async_session=db_async_session,
            user_repo=user_repo,
            verification_token_repo=verification_token_repo,
            email_service=email_service,
        )

        data = UserRegister(
            email="new@example.com",
            full_name="New User",
            password="Password123",
        )

        user_repo.get_user_by_email.return_value = None
        user_repo.create_one.return_value = None

        # Act / Assert
        with pytest.raises(FailedToCreateUserException):
            await auth_service.register(data)

        user_repo.create_one.assert_awaited_once()

        verification_token_repo.create_one.assert_not_awaited()
        db_async_session.commit.assert_not_awaited()
        email_service.send_verification_email.assert_not_awaited()

    async def test_register_hashes_password(self):
        # Arrange
        db_async_session = AsyncMock()
        user_repo = AsyncMock()
        verification_token_repo = AsyncMock()
        email_service = AsyncMock()

        auth_service = RegistrationService(
            db_async_session=db_async_session,
            user_repo=user_repo,
            verification_token_repo=verification_token_repo,
            email_service=email_service,
        )

        data = UserRegister(
            email="new@example.com",
            full_name="New User",
            password="Password123",
        )

        user = AsyncMock()
        user.id = 1
        user.email = data.email

        user_repo.get_user_by_email.return_value = None
        user_repo.create_one.return_value = user

        # Act
        await auth_service.register(data)

        # Assert
        user_data = user_repo.create_one.await_args.args[0]

        assert "password" not in user_data
        assert "hashed_password" in user_data
        assert user_data["hashed_password"] != data.password
        assert user_data["hashed_password"].startswith("$argon2")

    async def test_register_creates_verification_token(self):
        # Arrange
        db_async_session = AsyncMock()
        user_repo = AsyncMock()
        verification_token_repo = AsyncMock()
        email_service = AsyncMock()

        auth_service = RegistrationService(
            db_async_session=db_async_session,
            user_repo=user_repo,
            verification_token_repo=verification_token_repo,
            email_service=email_service,
        )

        data = UserRegister(
            email="new@example.com",
            full_name="New User",
            password="Password123",
        )

        user = AsyncMock()
        user.id = 1
        user.email = data.email

        user_repo.get_user_by_email.return_value = None
        user_repo.create_one.return_value = user

        # Act
        await auth_service.register(data)

        # Assert
        token_data = (
            verification_token_repo.create_one
            .await_args.args[0]
        )

        assert token_data["token"]
        assert token_data["user_id"] == user.id
        assert token_data["expires_at"] is not None

    async def test_register_verification_token_expires_in_24_hours(self):
        # Arrange
        db_async_session = AsyncMock()
        user_repo = AsyncMock()
        verification_token_repo = AsyncMock()
        email_service = AsyncMock()

        auth_service = RegistrationService(
            db_async_session=db_async_session,
            user_repo=user_repo,
            verification_token_repo=verification_token_repo,
            email_service=email_service,
        )

        data = UserRegister(
            email="new@example.com",
            full_name="New User",
            password="Password123",
        )

        user = AsyncMock()
        user.id = 1
        user.email = data.email

        user_repo.get_user_by_email.return_value = None
        user_repo.create_one.return_value = user

        before = datetime.now(timezone.utc)

        # Act
        await auth_service.register(data)

        after = datetime.now(timezone.utc)

        # Assert
        token_data = (
            verification_token_repo.create_one
            .await_args.args[0]
        )

        expires_at = token_data["expires_at"]

        assert (
            before + timedelta(hours=24)
            <= expires_at
            <= after + timedelta(hours=24)
        )

    async def test_register_failed_to_create_verification_token(
        self,
        monkeypatch,
    ):
        # Arrange
        db_async_session = AsyncMock()
        user_repo = AsyncMock()
        verification_token_repo = AsyncMock()
        email_service = AsyncMock()

        auth_service = RegistrationService(
            db_async_session=db_async_session,
            user_repo=user_repo,
            verification_token_repo=verification_token_repo,
            email_service=email_service,
        )

        data = UserRegister(
            email="new@example.com",
            full_name="New User",
            password="Password123",
        )

        user = AsyncMock()
        user.id = 1
        user.email = data.email

        user_repo.get_user_by_email.return_value = None
        user_repo.create_one.return_value = user

        monkeypatch.setattr(
            "app.features.auth.services.registration."
            "create_email_verification_token",
            lambda: None,
        )

        # Act / Assert
        with pytest.raises(FailedToCreateVerificationTokenException):
            await auth_service.register(data)

        verification_token_repo.create_one.assert_not_awaited()
        db_async_session.commit.assert_not_awaited()
        email_service.send_verification_email.assert_not_awaited()

    async def test_register_commits_transaction(self):
        # Arrange
        db_async_session = AsyncMock()
        user_repo = AsyncMock()
        verification_token_repo = AsyncMock()
        email_service = AsyncMock()

        auth_service = RegistrationService(
            db_async_session=db_async_session,
            user_repo=user_repo,
            verification_token_repo=verification_token_repo,
            email_service=email_service,
        )

        data = UserRegister(
            email="new@example.com",
            full_name="New User",
            password="Password123",
        )

        user = AsyncMock()
        user.id = 1
        user.email = data.email

        user_repo.get_user_by_email.return_value = None
        user_repo.create_one.return_value = user

        # Act
        await auth_service.register(data)

        # Assert
        db_async_session.commit.assert_awaited_once()

    async def test_register_sends_verification_email(self):
        # Arrange
        db_async_session = AsyncMock()
        user_repo = AsyncMock()
        verification_token_repo = AsyncMock()
        email_service = AsyncMock()

        auth_service = RegistrationService(
            db_async_session=db_async_session,
            user_repo=user_repo,
            verification_token_repo=verification_token_repo,
            email_service=email_service,
        )

        data = UserRegister(
            email="new@example.com",
            full_name="New User",
            password="Password123",
        )

        user = AsyncMock()
        user.id = 1
        user.email = data.email

        user_repo.get_user_by_email.return_value = None
        user_repo.create_one.return_value = user

        # Act
        await auth_service.register(data)

        # Assert
        email_service.send_verification_email.assert_awaited_once()

        email_data = (
            email_service.send_verification_email
            .await_args.kwargs
        )

        assert email_data["recipient"] == user.email
        assert email_data["token"]
