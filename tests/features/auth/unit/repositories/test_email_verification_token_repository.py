from datetime import datetime, timedelta, timezone

import pytest

from app.features.auth.repositories.email_verification_token import (
    EmailVerificationTokenRepository,
)


class TestEmailVerificationTokenRepository:

    @pytest.fixture
    def repository(self, db_session):
        return EmailVerificationTokenRepository(db_session)

    @pytest.fixture
    def verification_token_data(self, auth_user):
        return {
            "user_id": auth_user.id,
            "token": "verification-token-123",
            "expires_at": (
                datetime.now(timezone.utc)
                + timedelta(hours=24)
            ),
        }

    async def test_create_verification_token(
        self,
        repository,
        verification_token_data,
    ):
        token = await repository.create_verification_token(
            verification_token_data,
        )

        assert token is not None
        assert token.id is not None
        assert token.user_id == verification_token_data["user_id"]
        assert token.token == verification_token_data["token"]
        assert token.expires_at == verification_token_data["expires_at"]

    async def test_get_verification_token(
        self,
        repository,
        verification_token_data,
    ):
        await repository.create_verification_token(
            verification_token_data,
        )

        token = await repository.get_verification_token(
            verification_token_data["token"],
        )

        assert token is not None
        assert token.token == verification_token_data["token"]
        assert token.user_id == verification_token_data["user_id"]

    async def test_get_verification_token_not_found(
        self,
        repository,
    ):
        token = await repository.get_verification_token(
            "does-not-exist",
        )

        assert token is None

    async def test_get_verification_token_by_user_id(
        self,
        repository,
        verification_token_data,
    ):
        await repository.create_verification_token(
            verification_token_data,
        )

        token = await repository.get_verification_token_by_user_id(
            verification_token_data["user_id"],
        )

        assert token is not None
        assert token.user_id == verification_token_data["user_id"]
        assert token.token == verification_token_data["token"]

    async def test_get_verification_token_by_user_id_not_found(
        self,
        repository,
        auth_user,
    ):
        token = await repository.get_verification_token_by_user_id(
            auth_user.id,
        )

        assert token is None

    async def test_delete_verification_token_by_id(
        self,
        repository,
        verification_token_data,
    ):
        token = await repository.create_verification_token(
            verification_token_data,
        )

        deleted = await repository.delete_verification_token_by_id(
            token.id,
        )

        assert deleted is not None
        assert deleted.id == token.id

        result = await repository.get_verification_token(
            verification_token_data["token"],
        )

        assert result is None