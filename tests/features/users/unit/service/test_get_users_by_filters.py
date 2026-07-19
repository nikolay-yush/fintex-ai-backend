from app.features.users.models import User
from app.features.users.schemas import UserFilters
from app.features.users.service import UserService


class TestGetUsersByFilters:

    async def test_get_users_by_filters(
        self,
        user_service: UserService,
        user_repo_mock,
        user: User,
    ):
        # Arrange
        filters = UserFilters()
        user_repo_mock.get_users_by_filters.return_value = [user]

        # Act
        result = await user_service.get_users_by_filters(filters)

        # Assert
        user_repo_mock.get_users_by_filters.assert_awaited_once_with(
            filters,
        )
        assert result == [user]