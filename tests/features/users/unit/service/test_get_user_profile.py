from app.features.users.models import User
from app.features.users.service import UserService


class TestGetUserProfile:

    async def test_get_user_profile(
        self,
        user_service: UserService,
        user: User,
    ):
        # Act
        result = await user_service.get_user_profile(user)

        # Assert
        assert result == user