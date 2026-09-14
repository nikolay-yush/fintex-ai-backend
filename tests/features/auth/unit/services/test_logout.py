from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from app.features.auth.exceptions.refresh_token import (
    RefreshTokenNotFoundException,
)
from app.features.auth.services.logout import LogoutService


class TestLogout:
    @pytest.fixture
    def db_session(self):
        return AsyncMock()

    @pytest.fixture
    def refresh_token_repo(self):
        return Mock(
            get_refresh_token=AsyncMock(),
            revoke_refresh_token=AsyncMock(),
        )

    @pytest.fixture
    def service(self, db_session, refresh_token_repo):
        return LogoutService(
            db_async_session=db_session,
            refresh_token_repo=refresh_token_repo,
        )

    async def test_logout_success(
        self,
        service,
        db_session,
        refresh_token_repo,
    ):
        # Arrange
        refresh_token = "refresh-token"
        db_token = SimpleNamespace(id=1)

        refresh_token_repo.get_refresh_token.return_value = db_token
        refresh_token_repo.revoke_refresh_token.return_value = True

        # Act
        result = await service.logout(refresh_token)

        # Assert
        assert result is None

        refresh_token_repo.get_refresh_token.assert_awaited_once_with(
            refresh_token,
        )
        refresh_token_repo.revoke_refresh_token.assert_awaited_once_with(
            db_token.id,
        )
        db_session.commit.assert_awaited_once()

    async def test_logout_token_not_found(
        self,
        service,
        db_session,
        refresh_token_repo,
    ):
        # Arrange
        refresh_token = "unknown-token"
        refresh_token_repo.get_refresh_token.return_value = None

        # Act / Assert
        with pytest.raises(RefreshTokenNotFoundException):
            await service.logout(refresh_token)

        refresh_token_repo.get_refresh_token.assert_awaited_once_with(
            refresh_token,
        )
        refresh_token_repo.revoke_refresh_token.assert_not_awaited()
        db_session.commit.assert_not_awaited()

    async def test_logout_revoke_failed(
        self,
        service,
        db_session,
        refresh_token_repo,
    ):
        # Arrange
        refresh_token = "refresh-token"
        db_token = SimpleNamespace(id=1)

        refresh_token_repo.get_refresh_token.return_value = db_token
        refresh_token_repo.revoke_refresh_token.return_value = False

        # Act / Assert
        with pytest.raises(RefreshTokenNotFoundException):
            await service.logout(refresh_token)

        refresh_token_repo.revoke_refresh_token.assert_awaited_once_with(
            db_token.id,
        )
        db_session.commit.assert_not_awaited()


class TestLogoutAllUserSessions:
    @pytest.fixture
    def db_session(self):
        return AsyncMock()

    @pytest.fixture
    def refresh_token_repo(self):
        return Mock(
            revoke_all_user_tokens=AsyncMock(),
        )

    @pytest.fixture
    def service(self, db_session, refresh_token_repo):
        return LogoutService(
            db_async_session=db_session,
            refresh_token_repo=refresh_token_repo,
        )

    async def test_logout_all_user_sessions_success(
        self,
        service,
        db_session,
        refresh_token_repo,
    ):
        # Arrange
        user_id = 10

        refresh_token_repo.revoke_all_user_tokens.return_value = 3

        # Act
        result = await service.logout_all_user_sessions(user_id)

        # Assert
        assert result is None

        refresh_token_repo.revoke_all_user_tokens.assert_awaited_once_with(
            user_id,
        )
        db_session.commit.assert_awaited_once()

    async def test_logout_all_user_sessions_with_no_sessions(
        self,
        service,
        db_session,
        refresh_token_repo,
    ):
        # Arrange
        user_id = 10

        refresh_token_repo.revoke_all_user_tokens.return_value = 0

        # Act
        result = await service.logout_all_user_sessions(user_id)

        # Assert
        assert result is None

        refresh_token_repo.revoke_all_user_tokens.assert_awaited_once_with(
            user_id,
        )
        db_session.commit.assert_awaited_once()


class TestLogoutSession:
    @pytest.fixture
    def db_session(self):
        return AsyncMock()

    @pytest.fixture
    def refresh_token_repo(self):
        return Mock(
            get_token_family_for_user=AsyncMock(),
            revoke_token_family=AsyncMock(),
        )

    @pytest.fixture
    def service(self, db_session, refresh_token_repo):
        return LogoutService(
            db_async_session=db_session,
            refresh_token_repo=refresh_token_repo,
        )

    async def test_logout_session_success(
        self,
        service,
        db_session,
        refresh_token_repo,
    ):
        # Arrange
        token_family = "family-123"
        user_id = 10

        refresh_token_repo.get_token_family_for_user.return_value = (
            token_family
        )
        refresh_token_repo.revoke_token_family.return_value = 2

        # Act
        result = await service.logout_session(
            token_family=token_family,
            user_id=user_id,
        )

        # Assert
        assert result is None

        refresh_token_repo.get_token_family_for_user.assert_awaited_once_with(
            token_family=token_family,
            user_id=user_id,
        )
        refresh_token_repo.revoke_token_family.assert_awaited_once_with(
            token_family,
        )
        db_session.commit.assert_awaited_once()

    async def test_logout_session_family_not_found(
        self,
        service,
        db_session,
        refresh_token_repo,
    ):
        # Arrange
        token_family = "unknown-family"
        user_id = 10

        refresh_token_repo.get_token_family_for_user.return_value = None

        # Act / Assert
        with pytest.raises(RefreshTokenNotFoundException):
            await service.logout_session(
                token_family=token_family,
                user_id=user_id,
            )

        refresh_token_repo.get_token_family_for_user.assert_awaited_once_with(
            token_family=token_family,
            user_id=user_id,
        )
        refresh_token_repo.revoke_token_family.assert_not_awaited()
        db_session.commit.assert_not_awaited()

    async def test_logout_session_revoke_failed(
        self,
        service,
        db_session,
        refresh_token_repo,
    ):
        # Arrange
        token_family = "family-123"
        user_id = 10

        refresh_token_repo.get_token_family_for_user.return_value = (
            token_family
        )
        refresh_token_repo.revoke_token_family.return_value = 0

        # Act / Assert
        with pytest.raises(RefreshTokenNotFoundException):
            await service.logout_session(
                token_family=token_family,
                user_id=user_id,
            )

        refresh_token_repo.revoke_token_family.assert_awaited_once_with(
            token_family,
        )
        db_session.commit.assert_not_awaited()