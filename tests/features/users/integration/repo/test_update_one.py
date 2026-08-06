from app.features.users.models import User
from app.features.users.repository import UserRepository


class TestUpdateOne:
    async def test_success(self, user_repo: UserRepository, created_user_in_db: User):
        # Arrange

        # Act
        updated_user = await user_repo.update_one(
            created_user_in_db.id,
            {
                "full_name": "Updated User",
            },
        )

        # Assert
        assert updated_user is not None
        assert updated_user.id == created_user_in_db.id
        assert updated_user.email == created_user_in_db.email
        assert updated_user.full_name == "Updated User"

        db_updated_user = await user_repo.get_one_by_id(created_user_in_db.id)

        assert db_updated_user is not None
        assert db_updated_user.full_name == "Updated User"

    async def test_not_found(self, user_repo: UserRepository):
        # Arrange

        # Act
        updated_user = await user_repo.update_one(
            999999,
            {
                "full_name": "Updated User",
            },
        )

        # Assert
        assert updated_user is None
