from sqlalchemy.ext.asyncio import AsyncSession
import pytest

from app.features.auth.security import hash_password
from app.features.users.models import User
from app.features.users.repo import UserRepository
from tests.factories.user_factory import UserFactory


@pytest.fixture
def user_repo(db_session: AsyncSession) -> UserRepository:
    """Repository connected to the test database."""
    return UserRepository(db_session)


@pytest.fixture
async def created_user_in_db(
    user_repo: UserRepository,
) -> User:
    """Persist a user in the test database."""

    user = await user_repo.create_one(
        UserFactory.build_dict()
    )

    assert user is not None

    return user
