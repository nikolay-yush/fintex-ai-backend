from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.postgres.session import get_async_session

from app.features.users.repository import UsersRepository
from app.features.users.service import UsersService


def get_users_repo(
    db_async_session: AsyncSession = Depends(get_async_session),
) -> UsersRepository:
    return UsersRepository(db_async_session=db_async_session)

def get_users_service(
    db_async_session: AsyncSession = Depends(get_async_session),
    user_repo: UsersRepository = Depends(get_users_repo),
) -> UsersService:    
    return UsersService(
        db_async_session=db_async_session,
        user_repo=user_repo,
    )