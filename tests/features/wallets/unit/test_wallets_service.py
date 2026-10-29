import pytest
from decimal import Decimal
from fastapi import HTTPException

from app.features.wallets.enums import WalletType
from app.features.wallets.models import Wallet


class TestWalletsServiceUnit:
    """Unit tests for WalletsService grouped by methods."""

    # --- GET WALLET BY ID ---
    
    @pytest.mark.asyncio
    async def test_get_wallet_by_id_success(self, wallets_service, mock_wallets_repo, sample_wallet):
        """Test successful wallet retrieval by ID and user ID."""
        mock_wallets_repo.get_wallet_by_id_and_user.return_value = sample_wallet

        result = await wallets_service.get_wallet_by_id(
            wallet_id=sample_wallet.id, user_id=sample_wallet.user_id
        )

        assert result == sample_wallet
        mock_wallets_repo.get_wallet_by_id_and_user.assert_awaited_once_with(
            wallet_id=sample_wallet.id, user_id=sample_wallet.user_id
        )

    @pytest.mark.asyncio
    async def test_get_wallet_by_id_not_found(self, wallets_service, mock_wallets_repo):
        """Test wallet retrieval when the wallet does not exist or access is denied."""
        mock_wallets_repo.get_wallet_by_id_and_user.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await wallets_service.get_wallet_by_id(wallet_id=999, user_id=10)

        assert exc_info.value.status_code == 404
        assert "Wallet not found" in exc_info.value.detail

    # --- CREATE WALLET ---

    @pytest.mark.asyncio
    async def test_create_wallet_success(
        self, wallets_service, mock_wallets_repo, mock_db_session, sample_wallet_create_data
    ):
        """Test successful wallet creation."""
        user_id = 10
        
        created_wallet = Wallet(
            id=1,
            user_id=user_id,
            name=sample_wallet_create_data.name,
            type=sample_wallet_create_data.type,
            balance=sample_wallet_create_data.balance,
        )
        mock_wallets_repo.create.return_value = created_wallet

        result = await wallets_service.create_wallet(
            user_id=user_id, wallet_in=sample_wallet_create_data
        )

        assert result == created_wallet
        mock_db_session.commit.assert_awaited_once()
        mock_db_session.refresh.assert_awaited_once_with(created_wallet)

    # --- UPDATE WALLET ---

    @pytest.mark.asyncio
    async def test_update_wallet_success(
        self, wallets_service, mock_wallets_repo, mock_db_session, sample_wallet, sample_wallet_update_data
    ):
        """Test successful wallet update."""
        # First, mock that the wallet exists and belongs to the user
        mock_wallets_repo.get_wallet_by_id_and_user.return_value = sample_wallet

        result = await wallets_service.update_wallet(
            wallet_id=sample_wallet.id,
            user_id=sample_wallet.user_id,
            wallet_in=sample_wallet_update_data,
        )

        # Check that repository update method was called
        mock_wallets_repo.update.assert_awaited_once()
        mock_db_session.commit.assert_awaited_once()
        mock_db_session.refresh.assert_awaited_once_with(sample_wallet)

    # --- DELETE WALLET ---

    @pytest.mark.asyncio
    async def test_delete_wallet_success(
        self, wallets_service, mock_wallets_repo, mock_db_session, sample_wallet
    ):
        """Test successful wallet deletion."""
        mock_wallets_repo.get_wallet_by_id_and_user.return_value = sample_wallet

        await wallets_service.delete_wallet(
            wallet_id=sample_wallet.id, user_id=sample_wallet.user_id
        )

        mock_wallets_repo.delete.assert_awaited_once_with(db_async_session=mock_db_session, db_obj=sample_wallet)
        mock_db_session.commit.assert_awaited_once()