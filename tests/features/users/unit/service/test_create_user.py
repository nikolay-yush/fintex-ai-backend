from app.features.users.models import User
from app.features.users.schemas import UserCreate
from app.features.users.service import UserService


class TestCreateUser:

    async def test_create_user_success(
        self,
        user_service: UserService,
        user_repo_mock,
        user: User,
    ):
        # Arrange
        data = UserCreate(
            email=user.email,
            password="password123",
            full_name=user.full_name,
        )

        user_repo_mock.create_one.return_value = user

        # Act
        result = await user_service.create_user(data)

        # Assert
        user_repo_mock.create_one.assert_awaited_once_with(
            data.model_dump(),
        )
        assert result == user