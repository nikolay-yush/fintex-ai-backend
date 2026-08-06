from unittest.mock import AsyncMock

import pytest

from app.features.users.models import User
from app.features.users.repository import UserRepository
from app.features.users.service import UserService
from tests.factories.user_factory import UserFactory


@pytest.fixture
def user_repo_mock() -> AsyncMock:
    """Mock UserRepository."""
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def user_service(
    user_repo_mock: AsyncMock,
) -> UserService:
    """UserService with mocked repository."""
    return UserService(
        db_async_session=AsyncMock(),
        user_repo=user_repo_mock
    )


@pytest.fixture
def user() -> User:
    """User model without database."""
    return UserFactory.build_model(id=1)