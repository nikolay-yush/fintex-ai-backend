from typing import Annotated
from fastapi import APIRouter, Depends, Request, status

from app.core.security.rate_limit import rate_limit
from app.features.auth.dependencies import get_current_user, require_roles
from app.features.users.dependencies import get_users_service
from app.features.users.enums import UserRole
from app.features.users.service import UsersService
from app.features.users.models import User
from app.features.users.schemas import (
    UsersFilters,
    UsersListResponse,
    UserResponse,
    UserUpdateProfile,
)


users_router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# ---------- READ ----------

@users_router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
    summary="Get the current user's profile",
)
@rate_limit(max_requests=20, window_seconds=20, key_prefix="get_user_profile")
async def get_user_profile(
    request: Request,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
):
    return current_user


# (Admin Only) Read users with filters
@users_router.get(
    "",
    response_model=UsersListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a list of users",
)
@rate_limit(max_requests=30, window_seconds=20, key_prefix="admin_get_users")
async def get_users(
    request: Request,
    _: Annotated[
        User,
        Depends(require_roles(UserRole.ADMIN)),
    ],
    user_service: Annotated[
        UsersService,
        Depends(get_users_service),
    ],
    filters: Annotated[
        UsersFilters,
        Depends(),
    ],
):
    users, total = await user_service.get_users_by_filters(filters)

    return UsersListResponse(
        items=users,
        total=total,
        skip=filters.skip,
        limit=filters.limit,
    )


# ---------- UPDATE ----------

@users_router.patch(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user's profile",
)
@rate_limit(max_requests=10, window_seconds=60, key_prefix="update_user_profile")
async def update_user_profile(
    request: Request,
    data: UserUpdateProfile,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    user_service: Annotated[
        UsersService,
        Depends(get_users_service),
    ],
):
    return await user_service.update_user_profile(
        current_user=current_user,
        data=data,
    )


# ---------- DELETE ----------

@users_router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete current user's profile",
)
@rate_limit(max_requests=5, window_seconds=60, key_prefix="delete_user_profile")
async def delete_user_profile_by_user(
    request: Request,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    user_service: Annotated[
        UsersService,
        Depends(get_users_service),
    ],
):
    return await user_service.delete_user_by_id(
        user_id=current_user.id,
    )