from unittest.mock import AsyncMock

from fastapi import status

from app.features.auth.dependencies import get_auth_service
from app.features.auth.exceptions import (
    EmailVerificationTokenExpiredException,
    EmailVerificationTokenNotFoundException,
)
from app.features.auth.service import AuthService
from app.main import app


class TestVerifyEmail:

    async def test_verify_email_success(
        self,
        client,
    ):
        # Arrange
        auth_service = AsyncMock(spec=AuthService)

        app.dependency_overrides[get_auth_service] = (
            lambda: auth_service
        )

        # Act
        response = await client.post(
            "/api/v1/auth/verify-email",
            json={
                "token": "token",
            },
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK

        assert response.json() == {
            "message": "Email successfully verified",
        }

        auth_service.verify_email.assert_awaited_once_with(
            token="token",
        )

        app.dependency_overrides.clear()

    async def test_verify_email_not_found(
        self,
        client,
    ):
        # Arrange
        auth_service = AsyncMock(spec=AuthService)

        auth_service.verify_email.side_effect = (
            EmailVerificationTokenNotFoundException()
        )

        app.dependency_overrides[get_auth_service] = (
            lambda: auth_service
        )

        # Act
        response = await client.post(
            "/api/v1/auth/verify-email",
            json={
                "token": "token",
            },
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

        app.dependency_overrides.clear()

    async def test_verify_email_expired(
        self,
        client,
    ):
        # Arrange
        auth_service = AsyncMock(spec=AuthService)

        auth_service.verify_email.side_effect = (
            EmailVerificationTokenExpiredException()
        )

        app.dependency_overrides[get_auth_service] = (
            lambda: auth_service
        )

        # Act
        response = await client.post(
            "/api/v1/auth/verify-email",
            json={
                "token": "token",
            },
        )

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        app.dependency_overrides.clear()