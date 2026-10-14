from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.postgres.session import get_async_session
from app.features.wallets.repository import WalletsRepository
from app.features.wallets.service import WalletsService


def get_wallets_repo(
    db_async_session: AsyncSession = Depends(get_async_session),
) -> WalletsRepository:
    return WalletsRepository(db_async_session=db_async_session)


def get_wallets_service(
    db_async_session: AsyncSession = Depends(get_async_session),
    wallets_repo: WalletsRepository = Depends(get_wallets_repo),
) -> WalletsService:
    return WalletsService(
        db_async_session=db_async_session,
        wallets_repo=wallets_repo,
    )