from httpx import AsyncClient

from app.features.auth.security import create_access_token
from app.features.users.models import User


class TestUpdateUserProfile:

    async def test_update_user_profile_success(
        self,
        client: AsyncClient,
        auth_user: User,
    ):
        # Arrange
        token = create_access_token(auth_user.id)

        # Act
        response = await client.patch(
            "/api/v1/users/me",
            headers={
                "Authorization": f"Bearer {token}",
            },
            json={
                "full_name": "Updated Name",
            },
        )

        # Assert
        assert response.status_code == 200

        data = response.json()

        assert data["id"] == auth_user.id
        assert data["email"] == auth_user.email
        assert data["full_name"] == "Updated Name"

    async def test_update_user_profile_unauthorized(
        self,
        client: AsyncClient,
    ):
        # Act
        response = await client.patch(
            "/api/v1/users/me",
            json={
                "full_name": "Updated Name",
            },
        )

        # Assert
        assert response.status_code == 401

    async def test_update_user_profile_invalid_data(
        self,
        client: AsyncClient,
        auth_user: User,
    ):
        # Arrange
        token = create_access_token(auth_user.id)

        # Act
        response = await client.patch(
            "/api/v1/users/me",
            headers={
                "Authorization": f"Bearer {token}",
            },
            json={
                "full_name": "",
            },
        )

        # Assert
        assert response.status_code == 422