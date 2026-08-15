from typing import Annotated, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.features.users.enums import UserRole

from app.features.auth.security import decode_access_token
from app.features.users.models import User
from app.features.users.repository import UserRepository
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


def require_roles(
    *allowed_roles: UserRole,
) -> Callable:
    async def role_dependency(
        current_user: Annotated[
            User,
            Depends(get_current_user),
        ],
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return role_dependency