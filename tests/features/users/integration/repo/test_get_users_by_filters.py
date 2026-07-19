from app.features.users.models import User
from app.features.users.repo import UserRepository
from app.features.users.schemas import UserFilters
from tests.factories.user_factory import UserFactory


class TestGetUsersByFilters:

    async def test_filter_by_email(
        self,
        user_repo: UserRepository,
        created_user_in_db: User,
    ):
        # Arrange
        another_user = await user_repo.create_one(
            UserFactory.build_dict()
        )

        assert another_user is not None

        filters = UserFilters(
            email=created_user_in_db.email,
        )

        # Act
        users = await user_repo.get_users_by_filters(filters)

        # Assert
        assert len(users) == 1

        user = users[0]

        assert user.id == created_user_in_db.id
        assert user.email == created_user_in_db.email