from app.features.users.repo import UserRepository
from tests.factories.user_factory import UserFactory

from sqlalchemy.ext.asyncio import AsyncSession

async def test_create_one_success(db_session: AsyncSession):
    # Arrange
    repo = UserRepository(db_session)

    data = UserFactory.build_dict()

    # Act
    created_user = await repo.create_one(data)
    
    # Assert
    assert created_user is not None
    assert created_user.id is not None
    assert created_user.email == data["email"]
    assert created_user.full_name == data["full_name"]

    db_user = await repo.get_one_by_id(created_user.id)

    assert db_user is not None
    assert db_user.email == data["email"]