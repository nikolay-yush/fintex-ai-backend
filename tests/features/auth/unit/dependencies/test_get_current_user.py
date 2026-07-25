import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock

from app.features.auth.dependencies import get_current_user
from app.features.auth.security import create_access_token
from app.features.users.models import User


class TestGetCurrentUser:

    async def test_get_current_user_success(
        self,
        user: User,
    ):
        # Arrange
        user_repo = AsyncMock()

        token = create_access_token(user.id)

        user_repo.get_one_by_id.return_value = user

        # Act
        result = await get_current_user(
            token=token,
            user_repo=user_repo,
        )

        # Assert
        assert result == user

        user_repo.get_one_by_id.assert_awaited_once_with(
            model_id=user.id,
        )

    async def test_get_current_user_invalid_token(self):
        # Arrange
        user_repo = AsyncMock()

        # Act / Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                token="invalid_token",
                user_repo=user_repo,
            )

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid authentication credentials"

        user_repo.get_one_by_id.assert_not_awaited()

    async def test_get_current_user_user_not_found(self):
        # Arrange
        user_repo = AsyncMock()

        token = create_access_token(999999)

        user_repo.get_one_by_id.return_value = None

        # Act / Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                token=token,
                user_repo=user_repo,
            )

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "User not found"

        user_repo.get_one_by_id.assert_awaited_once_with(
            model_id=999999,
        )