from httpx import AsyncClient

from app.features.auth.security import create_access_token
from app.features.users.models import User


class TestAdminUsers:

    async def test_get_users_unauthorized(
        self,
        client: AsyncClient,
    ):
        # Act
        response = await client.get(
            "/api/v1/users",
        )

        # Assert
        assert response.status_code == 401

    async def test_get_users_forbidden(
        self,
        client: AsyncClient,
        auth_user: User,
    ):
        # Arrange
        token = create_access_token(auth_user.id)

        # Act
        response = await client.get(
            "/api/v1/users",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        # Assert
        assert response.status_code == 403
        assert response.json()["detail"] == (
            "Admin access required"
        )

    async def test_get_users_success(
        self,
        client: AsyncClient,
        admin_user: User,
    ):
        # Arrange
        token = create_access_token(admin_user.id)

        # Act
        response = await client.get(
            "/api/v1/users",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        # Assert
        assert response.status_code == 200

        data = response.json()

        assert isinstance(data, list)