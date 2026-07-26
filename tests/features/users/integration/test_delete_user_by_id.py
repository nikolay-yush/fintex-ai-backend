from httpx import AsyncClient

from app.features.auth.security import create_access_token
from app.features.users.models import User


class TestDeleteUserById:

    async def test_delete_user_success(
        self,
        client: AsyncClient,
        admin_user: User,
        auth_user: User,
    ):
        # Arrange
        token = create_access_token(admin_user.id)

        # Act
        response = await client.delete(
            f"/api/v1/users/{auth_user.id}",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        # Assert
        assert response.status_code == 204

    async def test_delete_user_unauthorized(
        self,
        client: AsyncClient,
        auth_user: User,
    ):
        # Act
        response = await client.delete(
            f"/api/v1/users/{auth_user.id}",
        )

        # Assert
        assert response.status_code == 401

    async def test_delete_user_forbidden(
        self,
        client: AsyncClient,
        auth_user: User,
    ):
        # Arrange
        token = create_access_token(auth_user.id)

        # Act
        response = await client.delete(
            f"/api/v1/users/{auth_user.id}",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        # Assert
        assert response.status_code == 403
        assert response.json()["detail"] == (
            "Admin access required"
        )

    async def test_delete_user_not_found(
        self,
        client: AsyncClient,
        admin_user: User,
    ):
        # Arrange
        token = create_access_token(admin_user.id)

        # Act
        response = await client.delete(
            "/api/v1/users/999999",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        # Assert
        assert response.status_code == 404