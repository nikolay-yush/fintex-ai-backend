from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.transactions.models import Transaction
from app.features.transactions.schemas import TransactionsFilters
from app.shared.base_crud import BaseCRUD


class TransactionsRepository(BaseCRUD[Transaction]):

    def __init__(self, db_async_session: AsyncSession) -> None:
        super().__init__(db_async_session=db_async_session, model=Transaction)

    async def get_transaction_by_id_and_wallet(
        self, transaction_id: int, wallet_id: int
    ) -> Transaction | None:
        """Get a specific transaction ensuring it belongs to the specified wallet."""
        query = select(self._model).where(
            self._model.id == transaction_id,
            self._model.wallet_id == wallet_id,
        )
        result = await self._db_async_session.execute(query)
        return result.scalar_one_or_none()

    async def get_transaction_by_idempotency_key(
        self, wallet_id: int, idempotency_key: str
    ) -> Transaction | None:
        """Find a transaction by idempotency key within a specific wallet (for safe retries)."""
        query = select(self._model).where(
            self._model.wallet_id == wallet_id,
            self._model.idempotency_key == idempotency_key,
        )
        result = await self._db_async_session.execute(query)
        return result.scalar_one_or_none()

    async def get_transactions_by_filters(
        self,
        wallet_id: int,
        filters: TransactionsFilters,
    ) -> tuple[list[Transaction], int]:
        """Get paginated and filtered list of transactions for a specific wallet."""
        query = select(Transaction).where(Transaction.wallet_id == wallet_id)

        # --- Filters ---
        if filters.name is not None:
            query = query.where(Transaction.name.ilike(f"%{filters.name}%"))

        if filters.type is not None:
            query = query.where(Transaction.type == filters.type)

        if filters.category_id is not None:
            query = query.where(Transaction.category_id == filters.category_id)

        if filters.amount_min is not None:
            query = query.where(Transaction.amount >= filters.amount_min)

        if filters.amount_max is not None:
            query = query.where(Transaction.amount <= filters.amount_max)

        if filters.recurrence_interval is not None:
            query = query.where(Transaction.recurrence_interval == filters.recurrence_interval)

        if filters.created_from is not None:
            query = query.where(Transaction.created_at >= filters.created_from)

        if filters.created_to is not None:
            query = query.where(Transaction.created_at <= filters.created_to)

        # --- Total count subquery ---
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self._db_async_session.execute(count_query)
        total = count_result.scalar_one() or 0

        # --- Sorting ---
        if filters.sort_by is not None:
            sort_column = getattr(Transaction, filters.sort_by, None)
            if sort_column is not None:
                if filters.sort_order == "desc":
                    query = query.order_by(sort_column.desc())
                else:
                    query = query.order_by(sort_column.asc())
        else:
            # Default sorting: newest first
            query = query.order_by(Transaction.id.desc())

        # --- Pagination ---
        query = query.offset(filters.skip)
        query = query.limit(filters.limit)

        result = await self._db_async_session.execute(query)
        transactions = list(result.scalars().all())

        return transactions, total

    async def create_transaction(self, data: dict[str, Any]) -> Transaction | None:
        return await super().create_one(data)

    async def update_transaction(
        self, transaction_id: int, data: dict[str, Any]
    ) -> Transaction | None:
        return await super().update_one(transaction_id, data)

    async def delete_transaction(self, transaction_id: int) -> Transaction | None:
        return await super().delete_one(transaction_id)