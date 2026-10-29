from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.features.wallets.repository import WalletsRepository
from app.features.wallets.schemas import WalletCreate, WalletUpdate, WalletsFilters
from app.features.wallets.models import Wallet
from app.features.wallets.schemas import WalletResponse


class WalletsService:
    def __init__(
        self,
        db_async_session: AsyncSession,
        wallets_repo: WalletsRepository,
    ) -> None:
        self._db_async_session = db_async_session
        self._wallets_repo = wallets_repo

    async def get_wallets(
        self, user_id: int, filters: WalletsFilters
    ) -> tuple[list[WalletResponse], int]:
        """Get filtered and paginated list of wallets for a specific user."""
        wallets, total = await self._wallets_repo.get_wallets_by_filters(user_id=user_id, filters=filters)
        response_wallets = [WalletResponse.model_validate(wallet) for wallet in wallets]
        return response_wallets, total


    async def get_wallet_by_id(self, wallet_id: int, user_id: int) -> WalletResponse | None:
        """Get a specific wallet ensuring it belongs to the user (Security check)."""
        wallet = await self._wallets_repo.get_wallet_by_id_and_user(wallet_id=wallet_id, user_id=user_id)
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found or access denied",
            )
        return WalletResponse.model_validate(wallet)

    async def create_wallet(self, user_id: int, data: WalletCreate) -> WalletResponse | None:
        """Create a new wallet for the user with zero balance."""
        wallet_data = data.model_dump()
        wallet_data["user_id"] = user_id  
        
        wallet = await self._wallets_repo.create_wallet(wallet_data)
        await self._db_async_session.commit()
        await self._db_async_session.refresh(wallet)
        return WalletResponse.model_validate(wallet) if wallet else None

    async def update_wallet(
        self, wallet_id: int, user_id: int, data: WalletUpdate
    ) -> WalletResponse | None:
        """Update wallet details with strict ownership verification."""
        wallet = await self.get_wallet_by_id(wallet_id=wallet_id, user_id=user_id)
        
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return wallet

        updated_wallet = await self._wallets_repo.update_wallet(wallet_id, update_data)
        await self._db_async_session.commit()
        await self._db_async_session.refresh(updated_wallet)
        return WalletResponse.model_validate(updated_wallet) if updated_wallet else None

    async def delete_wallet(self, wallet_id: int, user_id: int) -> bool:
        """Delete wallet with ownership verification."""
        await self.get_wallet_by_id(wallet_id=wallet_id, user_id=user_id)
        
        await self._wallets_repo.delete_wallet(wallet_id)
        await self._db_async_session.commit()
        return True