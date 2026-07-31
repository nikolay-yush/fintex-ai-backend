from unittest.mock import AsyncMock

from fastapi import status

from app.features.auth.dependencies import get_auth_service
from app.features.auth.exceptions import UserAlreadyExistsException
from app.features.auth.service import AuthService
from app.features.users.models import User
from app.main import app


class TestRegister:

    async def test_register_success(
        self,
        client,
        user: User,
    ):
        # Arrange
        auth_service = AsyncMock(
            spec=AuthService,
        )

        auth_service.register.return_value = user

        app.dependency_overrides[get_auth_service] = (
            lambda: auth_service
        )

        data = {
            "email": "new@example.com",
            "password": "Password123",
            "full_name": "New User",
        }

        # Act
        response = await client.post(
            "/api/v1/auth/register",
            json=data,
        )

        # Assert
        assert response.status_code == (
            status.HTTP_201_CREATED
        )

        response_data = response.json()

        assert response_data["id"] == user.id
        assert response_data["email"] == user.email
        assert response_data["full_name"] == user.full_name

        auth_service.register.assert_awaited_once()

        register_data = (
            auth_service.register.call_args.args[0]
        )

        assert register_data.email == data["email"]
        assert register_data.password == data["password"]
        assert register_data.full_name == data["full_name"]

        # Cleanup
        app.dependency_overrides.clear()

    async def test_register_user_already_exists(
        self,
        client,
    ):
        # Arrange
        auth_service = AsyncMock(
            spec=AuthService,
        )

        auth_service.register.side_effect = (
            UserAlreadyExistsException()
        )

        app.dependency_overrides[get_auth_service] = (
            lambda: auth_service
        )

        data = {
            "email": "existing@example.com",
            "password": "Password123",
            "full_name": "Existing User",
        }

        # Act
        response = await client.post(
            "/api/v1/auth/register",
            json=data,
        )

        # Assert
        assert response.status_code == (
            status.HTTP_409_CONFLICT
        )

        assert response.json()["detail"] == (
            "User with this email already exists"
        )

        auth_service.register.assert_awaited_once()

        # Cleanup
        app.dependency_overrides.clear()

    async def test_register_invalid_data(
        self,
        client,
    ):
        # Arrange
        auth_service = AsyncMock(
            spec=AuthService,
        )

        app.dependency_overrides[get_auth_service] = (
            lambda: auth_service
        )

        data = {
            "email": "invalid-email",
            "password": "123",
            "full_name": "",
        }

        # Act
        response = await client.post(
            "/api/v1/auth/register",
            json=data,
        )

        # Assert
        assert response.status_code == (
            status.HTTP_422_UNPROCESSABLE_CONTENT
        )

        auth_service.register.assert_not_awaited()

        # Cleanup
        app.dependency_overrides.clear()

