from app.features.users.models import User
from app.features.users.repository import UserRepository


class TestGetOneById:

    async def test_get_one_by_id_success(self, user_repo: UserRepository, created_user_in_db: User):
        # Arrange

        # Act
        user = await user_repo.get_one_by_id(created_user_in_db.id)

        # Assert
        assert user is not None
        assert user.id == created_user_in_db.id
        assert user.email == created_user_in_db.email
        assert user.full_name == created_user_in_db.full_name

    async def test_get_one_by_id_not_found(self, user_repo: UserRepository):
        # Arrange

        # Act
        user = await user_repo.get_one_by_id(999999)

        # Assert
        assert user is None