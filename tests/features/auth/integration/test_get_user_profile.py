from httpx import AsyncClient

from app.features.auth.security import create_access_token
from app.features.users.models import User


class TestGetUserProfile:

    async def test_get_user_profile_success(
        self,
        client: AsyncClient,
        auth_user: User,
    ):
        # Arrange
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": auth_user.email,
                "password": "Password123",
            },
        )

        assert login_response.status_code == 200

        token = login_response.json()["access_token"]

        # Act
        response = await client.get(
            "/api/v1/users/me",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        # Assert
        assert response.status_code == 200

        data = response.json()

        assert data["id"] == auth_user.id
        assert data["email"] == auth_user.email
        assert data["full_name"] == auth_user.full_name

    async def test_get_user_profile_unauthorized(
        self,
        client: AsyncClient,
    ):
        # Arrange
        # Act
        response = await client.get(
            "/api/v1/users/me",
        )

        # Assert
        assert response.status_code == 401

    async def test_get_user_profile_user_not_found(
        self,
        client: AsyncClient,
    ):
        # Arrange
        token = create_access_token(999999)

        # Act
        response = await client.get(
            "/api/v1/users/me",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        # Assert
        assert response.status_code == 401
        assert response.json()["detail"] == "User not found"