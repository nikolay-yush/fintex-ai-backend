from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from app.features.auth.exceptions.password_reset import (
    PasswordResetTokenExpiredException,
    PasswordResetTokenNotFoundException,
)
from app.features.auth.schemas.password_reset import PasswordResetConfirm
from app.features.auth.security import hash_password
from app.features.auth.services.password_reset import PasswordResetService


class TestRequestPasswordReset:
    @pytest.fixture
    def db_session(self):
        return AsyncMock()

    @pytest.fixture
    def user_repo(self):
        return Mock(
            get_user_by_email=AsyncMock(),
        )

    @pytest.fixture
    def password_reset_token_repo(self):
        return Mock(
            get_reset_token_by_user_id=AsyncMock(),
            delete_reset_token_by_id=AsyncMock(),
            create_reset_token=AsyncMock(),
        )

    @pytest.fixture
    def email_service(self):
        return Mock(
            send_reset_password_email=AsyncMock(),
        )

    @pytest.fixture
    def service(
        self,
        db_session,
        user_repo,
        password_reset_token_repo,
        email_service,
    ):
        return PasswordResetService(
            db_async_session=db_session,
            user_repo=user_repo,
            password_reset_token_repo=password_reset_token_repo,
            email_service=email_service,
        )

    async def test_request_password_reset_user_not_found(
        self,
        service,
        user_repo,
        password_reset_token_repo,
        db_session,
        email_service,
    ):
        # Arrange
        email = "unknown@example.com"
        user_repo.get_user_by_email.return_value = None

        # Act
        result = await service.request_password_reset(email)

        # Assert
        assert result is None

        user_repo.get_user_by_email.assert_awaited_once_with(email)
        password_reset_token_repo.get_reset_token_by_user_id.assert_not_awaited()
        password_reset_token_repo.create_reset_token.assert_not_awaited()
        db_session.commit.assert_not_awaited()
        email_service.send_reset_password_email.assert_not_awaited()

    async def test_request_password_reset_success_without_old_token(
        self,
        service,
        user_repo,
        password_reset_token_repo,
        db_session,
        email_service,
    ):
        # Arrange
        user = SimpleNamespace(
            id=1,
            email="user@example.com",
        )

        user_repo.get_user_by_email.return_value = user
        password_reset_token_repo.get_reset_token_by_user_id.return_value = (
            None
        )

        # Act
        result = await service.request_password_reset(
            user.email,
        )

        # Assert
        assert result is None

        user_repo.get_user_by_email.assert_awaited_once_with(
            user.email,
        )

        password_reset_token_repo.get_reset_token_by_user_id.assert_awaited_once_with(
            user.id,
        )

        password_reset_token_repo.delete_reset_token_by_id.assert_not_awaited()

        password_reset_token_repo.create_reset_token.assert_awaited_once()

        token_data = (
            password_reset_token_repo.create_reset_token.call_args.args[0]
        )

        assert token_data["user_id"] == user.id
        assert token_data["token"]
        assert token_data["created_at"] is not None
        assert token_data["expires_at"] > token_data["created_at"]

        db_session.commit.assert_awaited_once()

        email_service.send_reset_password_email.assert_awaited_once_with(
            recipient=user.email,
            token=token_data["token"],
        )

    async def test_request_password_reset_deletes_old_token(
        self,
        service,
        user_repo,
        password_reset_token_repo,
        db_session,
        email_service,
    ):
        # Arrange
        user = SimpleNamespace(
            id=1,
            email="user@example.com",
        )

        old_token = SimpleNamespace(id=100)

        user_repo.get_user_by_email.return_value = user
        password_reset_token_repo.get_reset_token_by_user_id.return_value = (
            old_token
        )

        # Act
        await service.request_password_reset(user.email)

        # Assert
        password_reset_token_repo.delete_reset_token_by_id.assert_awaited_once_with(
            old_token.id,
        )

        password_reset_token_repo.create_reset_token.assert_awaited_once()
        db_session.commit.assert_awaited_once()

        email_service.send_reset_password_email.assert_awaited_once()

    async def test_request_password_reset_token_expires_in_one_hour(
        self,
        service,
        user_repo,
        password_reset_token_repo,
    ):
        # Arrange
        user = SimpleNamespace(
            id=1,
            email="user@example.com",
        )

        user_repo.get_user_by_email.return_value = user
        password_reset_token_repo.get_reset_token_by_user_id.return_value = (
            None
        )

        # Act
        before = datetime.now(timezone.utc)

        await service.request_password_reset(user.email)

        after = datetime.now(timezone.utc)

        # Assert
        token_data = (
            password_reset_token_repo.create_reset_token.call_args.args[0]
        )

        expected_min = before + timedelta(hours=1)
        expected_max = after + timedelta(hours=1)

        assert expected_min <= token_data["expires_at"] <= expected_max


class TestResetPassword:
    @pytest.fixture
    def db_session(self):
        return AsyncMock()

    @pytest.fixture
    def user_repo(self):
        return Mock(
            get_one_by_id=AsyncMock(),
        )

    @pytest.fixture
    def password_reset_token_repo(self):
        return Mock(
            get_reset_token=AsyncMock(),
            delete_reset_token_by_id=AsyncMock(),
        )

    @pytest.fixture
    def email_service(self):
        return Mock(
            send_reset_password_email=AsyncMock(),
        )

    @pytest.fixture
    def service(
        self,
        db_session,
        user_repo,
        password_reset_token_repo,
        email_service,
    ):
        return PasswordResetService(
            db_async_session=db_session,
            user_repo=user_repo,
            password_reset_token_repo=password_reset_token_repo,
            email_service=email_service,
        )

    @pytest.fixture
    def reset_data(self):
        return PasswordResetConfirm(
            token="reset-token",
            password="NewPassword123",
        )

    async def test_reset_password_token_not_found(
        self,
        service,
        password_reset_token_repo,
        user_repo,
        db_session,
    ):
        # Arrange
        data = PasswordResetConfirm(
            token="unknown-token",
            password="NewPassword123",
        )

        password_reset_token_repo.get_reset_token.return_value = None

        # Act / Assert
        with pytest.raises(PasswordResetTokenNotFoundException):
            await service.reset_password(data)

        password_reset_token_repo.get_reset_token.assert_awaited_once_with(
            data.token,
        )
        user_repo.get_one_by_id.assert_not_awaited()
        password_reset_token_repo.delete_reset_token_by_id.assert_not_awaited()
        db_session.commit.assert_not_awaited()

    async def test_reset_password_token_expired(
        self,
        service,
        password_reset_token_repo,
        user_repo,
        db_session,
    ):
        # Arrange
        data = PasswordResetConfirm(
            token="expired-token",
            password="NewPassword123",
        )

        reset_token = SimpleNamespace(
            id=1,
            user_id=10,
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )

        password_reset_token_repo.get_reset_token.return_value = reset_token

        # Act / Assert
        with pytest.raises(PasswordResetTokenExpiredException):
            await service.reset_password(data)

        password_reset_token_repo.get_reset_token.assert_awaited_once_with(
            data.token,
        )
        user_repo.get_one_by_id.assert_not_awaited()
        password_reset_token_repo.delete_reset_token_by_id.assert_not_awaited()
        db_session.commit.assert_not_awaited()

    async def test_reset_password_user_not_found(
        self,
        service,
        password_reset_token_repo,
        user_repo,
        db_session,
    ):
        # Arrange
        data = PasswordResetConfirm(
            token="reset-token",
            password="NewPassword123",
        )

        reset_token = SimpleNamespace(
            id=1,
            user_id=10,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )

        password_reset_token_repo.get_reset_token.return_value = reset_token
        user_repo.get_one_by_id.return_value = None

        # Act
        result = await service.reset_password(data)

        # Assert
        assert result is None

        user_repo.get_one_by_id.assert_awaited_once_with(
            reset_token.user_id,
        )
        password_reset_token_repo.delete_reset_token_by_id.assert_not_awaited()
        db_session.commit.assert_not_awaited()

    async def test_reset_password_success(
        self,
        service,
        password_reset_token_repo,
        user_repo,
        db_session,
        reset_data,
    ):
        # Arrange
        user = SimpleNamespace(
            id=10,
            hashed_password=hash_password("OldPassword123"),
        )

        reset_token = SimpleNamespace(
            id=1,
            user_id=user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )

        password_reset_token_repo.get_reset_token.return_value = reset_token
        user_repo.get_one_by_id.return_value = user

        old_password_hash = user.hashed_password

        # Act
        result = await service.reset_password(reset_data)

        # Assert
        assert result is None

        assert user.hashed_password != old_password_hash
        assert user.hashed_password != reset_data.password

        password_reset_token_repo.get_reset_token.assert_awaited_once_with(
            reset_data.token,
        )

        user_repo.get_one_by_id.assert_awaited_once_with(
            reset_token.user_id,
        )

        password_reset_token_repo.delete_reset_token_by_id.assert_awaited_once_with(
            reset_token.id,
        )

        db_session.commit.assert_awaited_once()

    async def test_reset_password_hashes_new_password(
        self,
        service,
        password_reset_token_repo,
        user_repo,
        reset_data,
    ):
        # Arrange
        user = SimpleNamespace(
            id=10,
            hashed_password=hash_password("OldPassword123"),
        )

        reset_token = SimpleNamespace(
            id=1,
            user_id=user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )

        password_reset_token_repo.get_reset_token.return_value = reset_token
        user_repo.get_one_by_id.return_value = user

        # Act
        await service.reset_password(reset_data)

        # Assert
        from app.features.auth.security import verify_password

        assert verify_password(
            reset_data.password,
            user.hashed_password,
        )

    async def test_reset_password_deletes_token(
        self,
        service,
        password_reset_token_repo,
        user_repo,
        reset_data,
    ):
        # Arrange
        user = SimpleNamespace(id=10)

        reset_token = SimpleNamespace(
            id=55,
            user_id=user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )

        password_reset_token_repo.get_reset_token.return_value = reset_token
        user_repo.get_one_by_id.return_value = user

        # Act
        await service.reset_password(reset_data)

        # Assert
        password_reset_token_repo.delete_reset_token_by_id.assert_awaited_once_with(
            reset_token.id,
        )