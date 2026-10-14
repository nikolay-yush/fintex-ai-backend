from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.wallets.models import Wallet
from app.features.wallets.schemas import WalletsFilters
from app.shared.base_crud import BaseCRUD


class WalletsRepository(BaseCRUD[Wallet]):

    def __init__(self, db_async_session: AsyncSession) -> None:
        super().__init__(db_async_session=db_async_session, model=Wallet)

    async def get_wallet_by_id_and_user(
        self, wallet_id: int, user_id: int
    ) -> Wallet | None:
        """Get a specific wallet ensuring it belongs to the user."""
        query = select(self._model).where(
            self._model.id == wallet_id,
            self._model.user_id == user_id,
        )
        result = await self._db_async_session.execute(query)
        return result.scalar_one_or_none()

    async def get_wallets_by_filters(
        self,
        user_id: int,
        filters: WalletsFilters,
    ) -> tuple[list[Wallet], int]:
        """Get paginated and filtered list of wallets for a specific user."""
        query = select(Wallet).where(Wallet.user_id == user_id)

        # --- Filters ---
        if filters.name is not None:
            query = query.where(Wallet.name.ilike(f"%{filters.name}%"))

        if filters.type is not None:
            query = query.where(Wallet.type == filters.type)

        if filters.balance_min is not None:
            query = query.where(Wallet.balance >= filters.balance_min)

        if filters.balance_max is not None:
            query = query.where(Wallet.balance <= filters.balance_max)

        if filters.created_from is not None:
            query = query.where(Wallet.created_at >= filters.created_from)

        if filters.created_to is not None:
            query = query.where(Wallet.created_at <= filters.created_to)

        if filters.updated_from is not None:
            query = query.where(Wallet.updated_at >= filters.updated_from)

        if filters.updated_to is not None:
            query = query.where(Wallet.updated_at <= filters.updated_to)

        # --- Total count subquery ---
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self._db_async_session.execute(count_query)
        total = count_result.scalar_one() or 0

        # --- Sorting ---
        if filters.sort_by is not None:
            sort_column = getattr(Wallet, filters.sort_by, None)
            if sort_column is not None:
                if filters.sort_order == "desc":
                    query = query.order_by(sort_column.desc())
                else:
                    query = query.order_by(sort_column.asc())
        else:
            # Default sorting
            query = query.order_by(Wallet.id.desc())

        # --- Pagination ---
        query = query.offset(filters.skip)
        query = query.limit(filters.limit)

        result = await self._db_async_session.execute(query)
        wallets = list(result.scalars().all())

        return wallets, total

    async def create_wallet(self, data: dict[str, Any]) -> Wallet | None:
        return await super().create_one(data)

    async def update_wallet(
        self, wallet_id: int, data: dict[str, Any]
    ) -> Wallet | None:
        return await super().update_one(wallet_id, data)

    async def delete_wallet(self, wallet_id: int) -> Wallet | None:
        return await super().delete_one(wallet_id)