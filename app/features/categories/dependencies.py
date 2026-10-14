from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.postgres.session import get_async_session
from app.features.categories.repositories import CategoriesRepository
from app.features.categories.service import CategoriesService
from app.features.wallets.dependencies import get_wallets_repo
from app.features.wallets.repository import WalletsRepository


def get_categories_repo(
    db_async_session: AsyncSession = Depends(get_async_session),
) -> CategoriesRepository:
    return CategoriesRepository(db_async_session=db_async_session)


def get_categories_service(
    db_async_session: AsyncSession = Depends(get_async_session),
    categories_repo: CategoriesRepository = Depends(get_categories_repo),
    wallets_repo: WalletsRepository = Depends(get_wallets_repo),
) -> CategoriesService:
    return CategoriesService(
        db_async_session=db_async_session,
        categories_repo=categories_repo,
        wallets_repo=wallets_repo,
    )