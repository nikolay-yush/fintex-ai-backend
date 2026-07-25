from httpx import AsyncClient

from app.features.users.models import User


class TestLogin:

    async def test_login_success(
        self,
        client: AsyncClient,
        auth_user: User,
    ):
        # Act
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": auth_user.email,
                "password": "Password123",
            },
        )

        # Assert
        assert response.status_code == 200

        data = response.json()

        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_user_not_found(
        self,
        client: AsyncClient,
    ):
        # Act
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "notfound@example.com",
                "password": "Password123",
            },
        )

        # Assert
        assert response.status_code == 401

        data = response.json()

        assert data["detail"] == (
            "Invalid email or password"
        )

    async def test_login_wrong_password(
        self,
        client: AsyncClient,
        auth_user: User,
    ):
        # Act
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": auth_user.email,
                "password": "WrongPassword123",
            },
        )

        # Assert
        assert response.status_code == 401

        data = response.json()

        assert data["detail"] == (
            "Invalid email or password"
        )

    async def test_login_invalid_email(
        self,
        client: AsyncClient,
    ):
        # Act
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "invalid-email",
                "password": "Password123",
            },
        )

        # Assert
        assert response.status_code == 422