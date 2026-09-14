from datetime import datetime, timedelta, timezone

import pytest

from app.features.auth.models.refresh_token import RefreshToken
from app.features.auth.repositories.refresh_token import (
    RefreshTokenRepository,
)


class TestRefreshTokenRepository:

    @pytest.fixture
    def repository(self, db_session):
        return RefreshTokenRepository(db_session)

    @pytest.fixture
    def refresh_token_data(self, auth_user):
        return {
            "user_id": auth_user.id,
            "token": "refresh-token-123",
            "token_family": "family-123",
            "expires_at": datetime.now(timezone.utc)
            + timedelta(days=7),
        }

    async def test_create_refresh_token(
        self,
        repository,
        refresh_token_data,
    ):
        token = await repository.create_refresh_token(
            refresh_token_data,
        )

        assert token is not None
        assert token.id is not None
        assert token.user_id == refresh_token_data["user_id"]
        assert token.token == refresh_token_data["token"]
        assert token.token_family == refresh_token_data["token_family"]
        assert token.revoked_at is None

    async def test_get_refresh_token(
        self,
        repository,
        refresh_token_data,
    ):
        await repository.create_refresh_token(
            refresh_token_data,
        )

        token = await repository.get_refresh_token(
            refresh_token_data["token"],
        )

        assert token is not None
        assert token.token == refresh_token_data["token"]

    async def test_get_refresh_token_not_found(
        self,
        repository,
    ):
        token = await repository.get_refresh_token(
            "does-not-exist",
        )

        assert token is None

    async def test_get_refresh_token_by_user_id(
        self,
        repository,
        refresh_token_data,
    ):
        await repository.create_refresh_token(
            refresh_token_data,
        )

        token = await repository.get_refresh_token_by_user_id(
            refresh_token_data["user_id"],
        )

        assert token is not None
        assert token.user_id == refresh_token_data["user_id"]

    async def test_get_refresh_token_by_user_id_not_found(
        self,
        repository,
        auth_user,
    ):
        token = await repository.get_refresh_token_by_user_id(
            auth_user.id,
        )

        assert token is None

    async def test_delete_refresh_token(
        self,
        repository,
        refresh_token_data,
    ):
        await repository.create_refresh_token(
            refresh_token_data,
        )

        deleted = await repository.delete_refresh_token(
            refresh_token_data["token"],
        )

        assert deleted is True

        token = await repository.get_refresh_token(
            refresh_token_data["token"],
        )

        assert token is None

    async def test_delete_refresh_token_not_found(
        self,
        repository,
    ):
        deleted = await repository.delete_refresh_token(
            "does-not-exist",
        )

        assert deleted is False

    async def test_delete_refresh_token_by_id(
        self,
        repository,
        refresh_token_data,
    ):
        token = await repository.create_refresh_token(
            refresh_token_data,
        )

        deleted = await repository.delete_refresh_token_by_id(
            token.id,
        )

        assert deleted is not None

        result = await repository.get_refresh_token(
            refresh_token_data["token"],
        )

        assert result is None

    async def test_delete_all_refresh_tokens(
        self,
        repository,
        auth_user,
    ):
        for index in range(3):
            await repository.create_refresh_token(
                {
                    "user_id": auth_user.id,
                    "token": f"refresh-token-{index}",
                    "token_family": f"family-{index}",
                    "expires_at": datetime.now(timezone.utc)
                    + timedelta(days=7),
                }
            )

        deleted_count = await repository.delete_all_refresh_tokens(
            auth_user.id,
        )

        assert deleted_count == 3

        token = await repository.get_refresh_token_by_user_id(
            auth_user.id,
        )

        assert token is None

    async def test_revoke_refresh_token(
        self,
        repository,
        refresh_token_data,
    ):
        token = await repository.create_refresh_token(
            refresh_token_data,
        )

        revoked = await repository.revoke_refresh_token(
            token.id,
        )

        assert revoked is True

        result = await repository.get_refresh_token(
            refresh_token_data["token"],
        )

        assert result is not None
        assert result.revoked_at is not None

    async def test_revoke_refresh_token_twice(
        self,
        repository,
        refresh_token_data,
    ):
        token = await repository.create_refresh_token(
            refresh_token_data,
        )

        first_revoke = await repository.revoke_refresh_token(
            token.id,
        )

        second_revoke = await repository.revoke_refresh_token(
            token.id,
        )

        assert first_revoke is True
        assert second_revoke is False

    async def test_revoke_refresh_token_not_found(
        self,
        repository,
    ):
        revoked = await repository.revoke_refresh_token(
            999999,
        )

        assert revoked is False

    async def test_revoke_token_family(
        self,
        repository,
        auth_user,
    ):
        family = "family-123"

        for index in range(3):
            await repository.create_refresh_token(
                {
                    "user_id": auth_user.id,
                    "token": f"refresh-token-{index}",
                    "token_family": family,
                    "expires_at": datetime.now(timezone.utc)
                    + timedelta(days=7),
                }
            )

        revoked_count = await repository.revoke_token_family(
            family,
        )

        assert revoked_count == 3

    async def test_revoke_token_family_does_not_revoke_other_family(
        self,
        repository,
        auth_user,
    ):
        await repository.create_refresh_token(
            {
                "user_id": auth_user.id,
                "token": "token-family-a",
                "token_family": "family-a",
                "expires_at": datetime.now(timezone.utc)
                + timedelta(days=7),
            }
        )

        await repository.create_refresh_token(
            {
                "user_id": auth_user.id,
                "token": "token-family-b",
                "token_family": "family-b",
                "expires_at": datetime.now(timezone.utc)
                + timedelta(days=7),
            }
        )

        revoked_count = await repository.revoke_token_family(
            "family-a",
        )

        assert revoked_count == 1

        token_b = await repository.get_refresh_token(
            "token-family-b",
        )

        assert token_b is not None
        assert token_b.revoked_at is None

    async def test_revoke_all_user_tokens(
        self,
        repository,
        auth_user,
    ):
        for index in range(3):
            await repository.create_refresh_token(
                {
                    "user_id": auth_user.id,
                    "token": f"user-token-{index}",
                    "token_family": f"family-{index}",
                    "expires_at": datetime.now(timezone.utc)
                    + timedelta(days=7),
                }
            )

        revoked_count = await repository.revoke_all_user_tokens(
            auth_user.id,
        )

        assert revoked_count == 3

    async def test_revoke_all_user_tokens_does_not_affect_other_user(
        self,
        repository,
        auth_user,
        admin_user,
    ):
        await repository.create_refresh_token(
            {
                "user_id": auth_user.id,
                "token": "user-token",
                "token_family": "family-user",
                "expires_at": datetime.now(timezone.utc)
                + timedelta(days=7),
            }
        )

        await repository.create_refresh_token(
            {
                "user_id": admin_user.id,
                "token": "admin-token",
                "token_family": "family-admin",
                "expires_at": datetime.now(timezone.utc)
                + timedelta(days=7),
            }
        )

        revoked_count = await repository.revoke_all_user_tokens(
            auth_user.id,
        )

        assert revoked_count == 1

        admin_token = await repository.get_refresh_token(
            "admin-token",
        )

        assert admin_token is not None
        assert admin_token.revoked_at is None

    async def test_get_token_family_for_user(
        self,
        repository,
        refresh_token_data,
    ):
        await repository.create_refresh_token(
            refresh_token_data,
        )

        family = await repository.get_token_family_for_user(
            refresh_token_data["token_family"],
            refresh_token_data["user_id"],
        )

        assert family == refresh_token_data["token_family"]

    async def test_get_token_family_for_user_not_found(
        self,
        repository,
        auth_user,
    ):
        family = await repository.get_token_family_for_user(
            "does-not-exist",
            auth_user.id,
        )

        assert family is None

    async def test_get_token_family_for_user_ignores_revoked_token(
        self,
        repository,
        refresh_token_data,
    ):
        token = await repository.create_refresh_token(
            refresh_token_data,
        )

        await repository.revoke_refresh_token(
            token.id,
        )

        family = await repository.get_token_family_for_user(
            refresh_token_data["token_family"],
            refresh_token_data["user_id"],
        )

        assert family is None