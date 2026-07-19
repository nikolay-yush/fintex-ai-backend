from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.features.auth.dependencies import get_current_user
from app.features.users.dependencies import get_user_service
from app.features.users.models import User
from app.features.users.schemas import (
    UserFilters,
    UserResponse,
    UserUpdateProfile,
)
from app.features.users.service import UserService

users_router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# ---------- READ ----------

@users_router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def get_user_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    return await user_service.get_user_profile(current_user)


@users_router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def get_user_by_id(
    user_id: int,
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    return await user_service.get_user_by_id(user_id)


@users_router.get(
    "/",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
)
async def get_users(
    filters: Annotated[UserFilters, Query()],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    return await user_service.get_users_by_filters(filters)


# ---------- UPDATE ----------

@users_router.patch(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def update_user_profile(
    data: UserUpdateProfile,
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    return await user_service.update_user_profile(
        current_user=current_user,
        data=data,
    )


# ---------- DELETE ----------

@users_router.delete(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_user(
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    return await user_service.delete_user(current_user)