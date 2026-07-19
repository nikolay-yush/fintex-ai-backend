from app.features.users.models import User
from app.features.users.repo import UserRepository


class TestDeleteOne:

    async def test_success(self, user_repo: UserRepository, created_user_in_db: User):
        # Arrange

        # Act
        deleted_user = await user_repo.delete_one(created_user_in_db.id)

        # Assert
        assert deleted_user is not None
        assert deleted_user.id == created_user_in_db.id

        db_user_after_delete = await user_repo.get_one_by_id(created_user_in_db.id)
        assert db_user_after_delete is None

    async def test_not_found(self, user_repo: UserRepository):
        # Arrange

        # Act
        deleted_user = await user_repo.delete_one(999999)

        # Assert
        assert deleted_user is None