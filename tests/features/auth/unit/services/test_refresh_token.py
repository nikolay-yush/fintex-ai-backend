from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from app.features.auth.exceptions.authentication import (
    UserBannedException,
    UserInactiveException,
)
from app.features.auth.exceptions.refresh_token import (
    InvalidRefreshTokenException,
    RefreshTokenExpiredException,
)
from app.features.auth.schemas.authentication import TokenResponse
from app.features.auth.services.refresh_token import RefreshTokenService


class TestRefreshAccessToken:
    @pytest.fixture
    def db_session(self):
        return AsyncMock()

    @pytest.fixture
    def user_repo(self):
        return Mock(
            get_one_by_id=AsyncMock(),
        )

    @pytest.fixture
    def refresh_token_repo(self):
        return Mock(
            get_refresh_token=AsyncMock(),
            revoke_token_family=AsyncMock(),
            revoke_refresh_token=AsyncMock(),
            create_refresh_token=AsyncMock(),
        )

    @pytest.fixture
    def service(
        self,
        db_session,
        user_repo,
        refresh_token_repo,
    ):
        return RefreshTokenService(
            db_async_session=db_session,
            user_repo=user_repo,
            refresh_token_repo=refresh_token_repo,
        )

    @pytest.fixture
    def user(self):
        return SimpleNamespace(
            id=10,
            is_active=True,
            is_banned=False,
        )

    @pytest.fixture
    def db_refresh_token(self):
        return SimpleNamespace(
            id=100,
            token="refresh-token",
            token_family="family-123",
            user_id=10,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            created_at=datetime.now(timezone.utc),
            revoked_at=None,
        )

    async def test_refresh_access_token_success(
        self,
        service,
        db_session,
        user_repo,
        refresh_token_repo,
        user,
        db_refresh_token,
        monkeypatch,
    ):
        # Arrange
        refresh_token = "refresh-token"

        user_repo.get_one_by_id.return_value = user
        refresh_token_repo.get_refresh_token.return_value = (
            db_refresh_token
        )
        refresh_token_repo.revoke_refresh_token.return_value = True

        monkeypatch.setattr(
            "app.features.auth.services.refresh_token.decode_refresh_token",
            lambda token: user.id,
        )
        monkeypatch.setattr(
            "app.features.auth.services.refresh_token.create_refresh_token",
            lambda user_id: "new-refresh-token",
        )
        monkeypatch.setattr(
            "app.features.auth.services.refresh_token.create_access_token",
            lambda user_id: "new-access-token",
        )

        # Act
        result = await service.refresh_access_token(refresh_token)

        # Assert
        assert isinstance(result, TokenResponse)
        assert result.access_token == "new-access-token"
        assert result.refresh_token == "new-refresh-token"

        user_repo.get_one_by_id.assert_awaited_once_with(user.id)

        refresh_token_repo.get_refresh_token.assert_awaited_once_with(
            refresh_token,
        )

        refresh_token_repo.revoke_refresh_token.assert_awaited_once_with(
            db_refresh_token.id,
        )

        refresh_token_repo.create_refresh_token.assert_awaited_once()

        token_data = (
            refresh_token_repo.create_refresh_token.call_args.args[0]
        )

        assert token_data["token"] == "new-refresh-token"
        assert token_data["token_family"] == db_refresh_token.token_family
        assert token_data["user_id"] == user.id
        assert token_data["revoked_at"] is None

        db_session.commit.assert_awaited_once()

    async def test_refresh_invalid_jwt(
        self,
        service,
        refresh_token_repo,
        user_repo,
        db_session,
        monkeypatch,
    ):
        # Arrange
        monkeypatch.setattr(
            "app.features.auth.services.refresh_token.decode_refresh_token",
            lambda token: None,
        )

        # Act / Assert
        with pytest.raises(InvalidRefreshTokenException):
            await service.refresh_access_token("invalid-token")

        refresh_token_repo.get_refresh_token.assert_not_awaited()
        user_repo.get_one_by_id.assert_not_awaited()
        db_session.commit.assert_not_awaited()

    async def test_refresh_token_not_found(
        self,
        service,
        refresh_token_repo,
        user_repo,
        db_session,
        monkeypatch,
    ):
        # Arrange
        refresh_token = "unknown-token"

        monkeypatch.setattr(
            "app.features.auth.services.refresh_token.decode_refresh_token",
            lambda token: 10,
        )

        refresh_token_repo.get_refresh_token.return_value = None

        # Act / Assert
        with pytest.raises(InvalidRefreshTokenException):
            await service.refresh_access_token(refresh_token)

        refresh_token_repo.get_refresh_token.assert_awaited_once_with(
            refresh_token,
        )
        user_repo.get_one_by_id.assert_not_awaited()
        db_session.commit.assert_not_awaited()

    async def test_refresh_revoked_token_triggers_reuse_detection(
        self,
        service,
        refresh_token_repo,
        db_session,
        db_refresh_token,
        monkeypatch,
    ):
        # Arrange
        refresh_token = "refresh-token"

        db_refresh_token.revoked_at = datetime.now(timezone.utc)

        monkeypatch.setattr(
            "app.features.auth.services.refresh_token.decode_refresh_token",
            lambda token: db_refresh_token.user_id,
        )

        refresh_token_repo.get_refresh_token.return_value = (
            db_refresh_token
        )

        # Act / Assert
        with pytest.raises(InvalidRefreshTokenException):
            await service.refresh_access_token(refresh_token)

        refresh_token_repo.revoke_token_family.assert_awaited_once_with(
            db_refresh_token.token_family,
        )

        db_session.commit.assert_awaited_once()

        refresh_token_repo.revoke_refresh_token.assert_not_awaited()
        refresh_token_repo.create_refresh_token.assert_not_awaited()

    async def test_refresh_token_expired(
        self,
        service,
        refresh_token_repo,
        user_repo,
        db_session,
        db_refresh_token,
        monkeypatch,
    ):
        # Arrange
        db_refresh_token.expires_at = (
            datetime.now(timezone.utc) - timedelta(minutes=1)
        )

        monkeypatch.setattr(
            "app.features.auth.services.refresh_token.decode_refresh_token",
            lambda token: db_refresh_token.user_id,
        )

        refresh_token_repo.get_refresh_token.return_value = (
            db_refresh_token
        )

        # Act / Assert
        with pytest.raises(RefreshTokenExpiredException):
            await service.refresh_access_token("refresh-token")

        user_repo.get_one_by_id.assert_not_awaited()
        refresh_token_repo.revoke_refresh_token.assert_not_awaited()
        refresh_token_repo.create_refresh_token.assert_not_awaited()
        db_session.commit.assert_not_awaited()

    async def test_refresh_user_not_found(
        self,
        service,
        refresh_token_repo,
        user_repo,
        db_session,
        db_refresh_token,
        monkeypatch,
    ):
        # Arrange
        monkeypatch.setattr(
            "app.features.auth.services.refresh_token.decode_refresh_token",
            lambda token: db_refresh_token.user_id,
        )

        refresh_token_repo.get_refresh_token.return_value = (
            db_refresh_token
        )
        user_repo.get_one_by_id.return_value = None

        # Act / Assert
        with pytest.raises(Exception) as exc_info:
            await service.refresh_access_token("refresh-token")

        assert exc_info.type.__name__ == "UserNotFoundException"

        refresh_token_repo.revoke_refresh_token.assert_not_awaited()
        refresh_token_repo.create_refresh_token.assert_not_awaited()
        db_session.commit.assert_not_awaited()

    async def test_refresh_inactive_user(
        self,
        service,
        refresh_token_repo,
        user_repo,
        db_session,
        user,
        db_refresh_token,
        monkeypatch,
    ):
        # Arrange
        user.is_active = False

        monkeypatch.setattr(
            "app.features.auth.services.refresh_token.decode_refresh_token",
            lambda token: user.id,
        )

        refresh_token_repo.get_refresh_token.return_value = (
            db_refresh_token
        )
        user_repo.get_one_by_id.return_value = user

        # Act / Assert
        with pytest.raises(UserInactiveException):
            await service.refresh_access_token("refresh-token")

        refresh_token_repo.revoke_refresh_token.assert_not_awaited()
        refresh_token_repo.create_refresh_token.assert_not_awaited()
        db_session.commit.assert_not_awaited()

    async def test_refresh_banned_user(
        self,
        service,
        refresh_token_repo,
        user_repo,
        db_session,
        user,
        db_refresh_token,
        monkeypatch,
    ):
        # Arrange
        user.is_banned = True

        monkeypatch.setattr(
            "app.features.auth.services.refresh_token.decode_refresh_token",
            lambda token: user.id,
        )

        refresh_token_repo.get_refresh_token.return_value = (
            db_refresh_token
        )
        user_repo.get_one_by_id.return_value = user

        # Act / Assert
        with pytest.raises(UserBannedException):
            await service.refresh_access_token("refresh-token")

        refresh_token_repo.revoke_refresh_token.assert_not_awaited()
        refresh_token_repo.create_refresh_token.assert_not_awaited()
        db_session.commit.assert_not_awaited()

    async def test_refresh_atomic_rotation_failed(
        self,
        service,
        refresh_token_repo,
        user_repo,
        db_session,
        user,
        db_refresh_token,
        monkeypatch,
    ):
        # Arrange
        monkeypatch.setattr(
            "app.features.auth.services.refresh_token.decode_refresh_token",
            lambda token: user.id,
        )

        refresh_token_repo.get_refresh_token.return_value = (
            db_refresh_token
        )
        user_repo.get_one_by_id.return_value = user
        refresh_token_repo.revoke_refresh_token.return_value = False

        # Act / Assert
        with pytest.raises(InvalidRefreshTokenException):
            await service.refresh_access_token("refresh-token")

        refresh_token_repo.revoke_refresh_token.assert_awaited_once_with(
            db_refresh_token.id,
        )

        refresh_token_repo.create_refresh_token.assert_not_awaited()
        db_session.commit.assert_not_awaited()

    async def test_refresh_keeps_same_token_family(
        self,
        service,
        refresh_token_repo,
        user_repo,
        db_refresh_token,
        user,
        monkeypatch,
    ):
        # Arrange
        monkeypatch.setattr(
            "app.features.auth.services.refresh_token.decode_refresh_token",
            lambda token: user.id,
        )
        monkeypatch.setattr(
            "app.features.auth.services.refresh_token.create_refresh_token",
            lambda user_id: "new-refresh-token",
        )
        monkeypatch.setattr(
            "app.features.auth.services.refresh_token.create_access_token",
            lambda user_id: "new-access-token",
        )

        refresh_token_repo.get_refresh_token.return_value = (
            db_refresh_token
        )
        user_repo.get_one_by_id.return_value = user
        refresh_token_repo.revoke_refresh_token.return_value = True

        # Act
        await service.refresh_access_token("refresh-token")

        # Assert
        token_data = (
            refresh_token_repo.create_refresh_token.call_args.args[0]
        )

        assert token_data["token_family"] == db_refresh_token.token_family
        assert token_data["user_id"] == user.id

    async def test_refresh_new_token_is_not_revoked(
        self,
        service,
        refresh_token_repo,
        user_repo,
        db_refresh_token,
        user,
        monkeypatch,
    ):
        # Arrange
        monkeypatch.setattr(
            "app.features.auth.services.refresh_token.decode_refresh_token",
            lambda token: user.id,
        )
        monkeypatch.setattr(
            "app.features.auth.services.refresh_token.create_refresh_token",
            lambda user_id: "new-refresh-token",
        )
        monkeypatch.setattr(
            "app.features.auth.services.refresh_token.create_access_token",
            lambda user_id: "new-access-token",
        )

        refresh_token_repo.get_refresh_token.return_value = (
            db_refresh_token
        )
        user_repo.get_one_by_id.return_value = user
        refresh_token_repo.revoke_refresh_token.return_value = True

        # Act
        await service.refresh_access_token("refresh-token")

        # Assert
        token_data = (
            refresh_token_repo.create_refresh_token.call_args.args[0]
        )

        assert token_data["revoked_at"] is None