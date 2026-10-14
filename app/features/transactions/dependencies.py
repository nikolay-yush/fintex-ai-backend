from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.postgres.session import get_async_session
from app.features.transactions.repositories import TransactionsRepository
from app.features.transactions.service import TransactionsService
from app.features.wallets.repository import WalletsRepository
from app.features.wallets.dependencies import get_wallets_repo
from app.features.categories.repositories import CategoriesRepository
from app.features.categories.dependencies import get_categories_repo


def get_transactions_repo(
    db_async_session: AsyncSession = Depends(get_async_session),
) -> TransactionsRepository:
    return TransactionsRepository(db_async_session=db_async_session)


def get_transactions_service(
    db_async_session: AsyncSession = Depends(get_async_session),
    transactions_repo: TransactionsRepository = Depends(get_transactions_repo),
    wallets_repo: WalletsRepository = Depends(get_wallets_repo),
    categories_repo: CategoriesRepository = Depends(get_categories_repo),
) -> TransactionsService:
    return TransactionsService(
        db_async_session=db_async_session,
        transactions_repo=transactions_repo,
        wallets_repo=wallets_repo,
        categories_repo=categories_repo,
    )