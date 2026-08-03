from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.postgres.session import get_async_session
from app.core.email.sender import SMTPEmailSender
from app.core.email.renderer import EmailRenderer
from app.core.email.service import EmailService
from app.features.auth.repo import AuthRepository
from app.features.users.enums import UserRole

from app.features.auth.security import decode_access_token
from app.features.auth.service import AuthService
from app.features.users.models import User
from app.features.users.repo import UserRepository
from app.features.users.dependencies import get_user_repo

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repo: Annotated[
        UserRepository,
        Depends(get_user_repo),
    ],
) -> User:
    """Return the currently authenticated user."""

    user_id = decode_access_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_repo.get_one_by_id(
        model_id=user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is banned",
        )

    return user

async def get_current_admin(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> User:
    """Return the current user if they have admin privileges."""

    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user


def get_auth_repo(
    db_async_session: AsyncSession = Depends(get_async_session),
) -> AuthRepository:
    return AuthRepository(db_async_session=db_async_session)


def get_email_sender() -> SMTPEmailSender:
    return SMTPEmailSender()

def get_email_renderer() -> EmailRenderer:
    return EmailRenderer()

def get_email_service(
    sender: SMTPEmailSender = Depends(get_email_sender),
    renderer: EmailRenderer = Depends(get_email_renderer),
) -> EmailService:
    return EmailService(sender=sender, renderer=renderer)


def get_auth_service(
    db_async_session: AsyncSession = Depends(get_async_session),
    email_service: EmailService = Depends(get_email_service)
) -> AuthService:
    auth_repo: AuthRepository = AuthRepository(db_async_session=db_async_session)
    user_repo: UserRepository = UserRepository(db_async_session=db_async_session)
    

    return AuthService(
        db_async_session=db_async_session,
        auth_repo=auth_repo,
        user_repo=user_repo,
        email_service=email_service,
    )