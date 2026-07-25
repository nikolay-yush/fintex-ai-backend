import pytest
import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from app.features.auth.security import hash_password
from app.features.users.models import User
from tests.factories.user_factory import UserFactory


@pytest.fixture
def user() -> User:
    """Return a user model for Auth unit tests."""
    return UserFactory.build_model(id=1)


@pytest_asyncio.fixture
async def auth_user(
    db_session: AsyncSession,
) -> User:
    user = User(
        email="auth@example.com",
        full_name="Auth Test User",
        hashed_password=hash_password("Password123"),
    )

    db_session.add(user)

    await db_session.commit()
    await db_session.refresh(user)

    return user