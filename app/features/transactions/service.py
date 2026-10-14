from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.features.transactions.repositories import TransactionsRepository
from app.features.transactions.schemas import (
    TransactionCreate,
    TransactionUpdate,
    TransactionsFilters,
)
from app.features.transactions.models import Transaction
from app.features.wallets.repository import WalletsRepository
from app.features.categories.repositories import CategoriesRepository


class TransactionsService:
    def __init__(
        self,
        db_async_session: AsyncSession,
        transactions_repo: TransactionsRepository,
        wallets_repo: WalletsRepository,
        categories_repo: CategoriesRepository,
    ) -> None:
        self._db_async_session = db_async_session
        self._transactions_repo = transactions_repo
        self._wallets_repo = wallets_repo
        self._categories_repo = categories_repo

    async def _verify_wallet_ownership(self, wallet_id: int, user_id: int) -> None:
        """Helper to check if the wallet exists and belongs to the user."""
        wallet = await self._wallets_repo.get_wallet_by_id_and_user(wallet_id=wallet_id, user_id=user_id)
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found or access denied",
            )

    async def get_transactions(
        self, wallet_id: int, user_id: int, filters: TransactionsFilters
    ) -> tuple[list[Transaction], int]:
        """Get filtered and paginated list of transactions for a specific wallet."""
        await self._verify_wallet_ownership(wallet_id=wallet_id, user_id=user_id)
        return await self._transactions_repo.get_transactions_by_filters(wallet_id=wallet_id, filters=filters)

    async def get_transaction_by_id(
        self, transaction_id: int, wallet_id: int, user_id: int
    ) -> Transaction:
        """Get a specific transaction ensuring ownership through the wallet."""
        await self._verify_wallet_ownership(wallet_id=wallet_id, user_id=user_id)

        transaction = await self._transactions_repo.get_transaction_by_id_and_wallet(
            transaction_id=transaction_id, wallet_id=wallet_id
        )
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found in this wallet",
            )
        return transaction

    async def create_transaction(
        self, wallet_id: int, user_id: int, data: TransactionCreate
    ) -> Transaction | None:
        """Create a new transaction within a verified wallet with idempotency and category checks."""
        await self._verify_wallet_ownership(wallet_id=wallet_id, user_id=user_id)

        # 1. Проверяем идемпотентность (если транзакция с таким ключом уже существует)
        existing_tx = await self._transactions_repo.get_transaction_by_idempotency_key(
            wallet_id=wallet_id, idempotency_key=data.idempotency_key
        )
        if existing_tx:
            return existing_tx

        # 2. Проверяем, существует ли категория и принадлежит ли она данному кошельку
        category = await self._categories_repo.get_category_by_id_and_wallet(
            category_id=data.category_id, wallet_id=wallet_id
        )
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found or does not belong to this wallet",
            )

        # 3. Подготавливаем данные для создания
        tx_data = data.model_dump()
        tx_data["wallet_id"] = wallet_id

        try:
            transaction = await self._transactions_repo.create_transaction(tx_data)
            await self._db_async_session.commit()
            await self._db_async_session.refresh(transaction)
            return transaction

        except IntegrityError:
            await self._db_async_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transaction with this idempotency key or invalid data already exists",
            )

    async def update_transaction(
        self, transaction_id: int, wallet_id: int, user_id: int, data: TransactionUpdate
    ) -> Transaction | None:
        """Update transaction details with strict ownership and category verification."""
        transaction = await self.get_transaction_by_id(
            transaction_id=transaction_id, wallet_id=wallet_id, user_id=user_id
        )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return transaction

        # Если в запросе на обновление передана новая категория — проверяем ее принадлежность кошельку
        if "category_id" in update_data:
            category = await self._categories_repo.get_category_by_id_and_wallet(
                category_id=update_data["category_id"], wallet_id=wallet_id
            )
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="New category not found or does not belong to this wallet",
                )

        try:
            updated_transaction = await self._transactions_repo.update_transaction(
                transaction_id, update_data
            )
            await self._db_async_session.commit()
            await self._db_async_session.refresh(updated_transaction)
            return updated_transaction

        except IntegrityError:
            await self._db_async_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update transaction due to database constraints",
            )

    async def delete_transaction(self, transaction_id: int, wallet_id: int, user_id: int) -> bool:
        """Delete transaction with ownership verification."""
        await self.get_transaction_by_id(
            transaction_id=transaction_id, wallet_id=wallet_id, user_id=user_id
        )

        await self._transactions_repo.delete_transaction(transaction_id)
        await self._db_async_session.commit()
        return True