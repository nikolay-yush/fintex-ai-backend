from app.features.users.models import User
from app.features.users.schemas import UserUpdateProfile
from app.features.users.service import UserService
from tests.factories.user_factory import UserFactory


class TestUpdateUserProfile:

    async def test_update_user_profile_success(
        self,
        user_service: UserService,
        user_repo_mock,
        user: User,
    ):
        # Arrange
        data = UserUpdateProfile(
            full_name="Updated User",
        )

        updated_user = UserFactory.build_model(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            full_name="Updated User",
        )

        user_repo_mock.update_one.return_value = updated_user

        # Act
        result = await user_service.update_user_profile(
            user,
            data,
        )

        # Assert
        user_repo_mock.update_one.assert_awaited_once_with(
            user.id,
            data.model_dump(),
        )
        assert result == updated_user