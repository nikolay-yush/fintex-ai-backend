import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.security import hash_password
from app.features.users.enums import UserRole
from app.features.users.models import User
from tests.factories.user_factory import UserFactory


@pytest_asyncio.fixture
async def auth_user(
    db_session: AsyncSession,
) -> User:
    """Create and return an authenticated test user."""

    user = UserFactory.build_model(
        email="auth@example.com",
        full_name="Auth Test User",
        hashed_password=hash_password("Password123"),
        role=UserRole.USER,
    )

    db_session.add(user)

    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest_asyncio.fixture
async def admin_user(
    db_session: AsyncSession,
) -> User:
    """Create and return an admin test user."""

    user = UserFactory.build_model(
        email="admin@example.com",
        full_name="Admin Test User",
        hashed_password=hash_password("Password123"),
        role=UserRole.ADMIN,
    )

    db_session.add(user)

    await db_session.commit()
    await db_session.refresh(user)

    return user