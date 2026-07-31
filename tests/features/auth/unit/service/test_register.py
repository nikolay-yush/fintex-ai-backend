import pytest
from unittest.mock import AsyncMock

from app.features.auth.exceptions import UserAlreadyExistsException
from app.features.auth.schemas import UserRegister
from app.features.auth.service import AuthService
from app.features.users.models import User


class TestRegister:

    async def test_register_success(
        self,
        user: User,
    ):
        # Arrange
        user_repo = AsyncMock()
        auth_repo = AsyncMock()

        auth_service = AuthService(
            db_async_session=AsyncMock(),
            user_repo=user_repo,
            auth_repo=auth_repo,
        )

        data = UserRegister(
            email="new@example.com",
            password="Password123",
            full_name="New User",
        )

        user_repo.get_user_by_email.return_value = None
        user_repo.create_one.return_value = user

        # Act
        result = await auth_service.register(data)

        # Assert
        assert result == user

        user_repo.get_user_by_email.assert_awaited_once_with(
            data.email,
        )

        user_repo.create_one.assert_awaited_once()

        created_user_data = (
            user_repo.create_one.call_args.args[0]
        )

        assert created_user_data["email"] == data.email
        assert created_user_data["full_name"] == data.full_name
        assert "password" not in created_user_data
        assert "hashed_password" in created_user_data

        # Verification token
        auth_repo.create_one.assert_awaited_once()

        created_token_data = (
            auth_repo.create_one.call_args.args[0]
        )

        assert created_token_data["user_id"] == user.id
        assert created_token_data["token"]
        assert created_token_data["expires_at"] is not None

    async def test_register_user_already_exists(
        self,
    ):
        # Arrange
        user_repo = AsyncMock()
        auth_repo = AsyncMock()

        auth_service = AuthService(
            db_async_session=AsyncMock(),
            user_repo=user_repo,
            auth_repo=auth_repo,
        )

        data = UserRegister(
            email="existing@example.com",
            password="Password123",
            full_name="Existing User",
        )

        existing_user = User(
            id=1,
            email=data.email,
            hashed_password="hashed_password",
            full_name=data.full_name,
        )

        user_repo.get_user_by_email.return_value = (
            existing_user
        )

        # Act / Assert
        with pytest.raises(
            UserAlreadyExistsException,
        ):
            await auth_service.register(data)

        user_repo.get_user_by_email.assert_awaited_once_with(
            data.email,
        )

        user_repo.create_one.assert_not_awaited()

        # Verification token must not be created
        auth_repo.create_one.assert_not_awaited()

