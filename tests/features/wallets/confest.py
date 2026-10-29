from decimal import Decimal
import pytest
from unittest.mock import AsyncMock

from app.features.wallets.models import Wallet
from app.features.wallets.enums import WalletType
from app.features.wallets.service import WalletsService
from app.features.wallets.schemas import WalletCreate, WalletUpdate


@pytest.fixture
def mock_db_session():
    """Mock for async database session (for isolation in unit tests)."""
    session = AsyncMock()
    return session


@pytest.fixture
def mock_wallets_repo():
    """Mock for wallets repository (replaces real database calls)."""
    return AsyncMock()


@pytest.fixture
def wallets_service(mock_db_session, mock_wallets_repo):
    """Ready-to-use WalletsService instance with injected mocks."""
    return WalletsService(
        db_async_session=mock_db_session,
        wallets_repo=mock_wallets_repo,
    )


@pytest.fixture
def sample_wallet():
    """Sample ready wallet object (SQLAlchemy model) matching the model fields."""
    return Wallet(
        id=1,
        user_id=10,
        name="Main Card",
        type=WalletType.SPENDINGS, 
        balance=Decimal("1500.00"),  # Using Decimal for balance
    )


@pytest.fixture
def sample_wallet_create_data():
    """Data payload for creating a new wallet (Pydantic schema)."""
    return WalletCreate(
        name="Savings",
        type=WalletType.SPENDINGS,
    )


@pytest.fixture
def sample_wallet_update_data():
    """Data payload for updating an existing wallet (Pydantic schema)."""
    return WalletUpdate(
        name="Updated Wallet Name",
        type=WalletType.SPENDINGS
    )