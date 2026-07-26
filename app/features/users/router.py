from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.features.auth.dependencies import get_current_admin, get_current_user
from app.features.users.dependencies import get_user_service
from app.features.users.service import UserService
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

@users_router.get("/me", response_model=UserResponse)
async def get_user_profile(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ]
):
    return current_user


# read users with filters (admin only)
@users_router.get("", response_model=list[UserResponse])
async def get_users(
    _: Annotated[
        User,
        Depends(get_current_admin),
    ],
    user_service: Annotated[
        UserService,
        Depends(get_user_service),
    ],
    filters: Annotated[
        UserFilters,
        Depends(),
    ],
):
    return await user_service.get_users_by_filters(filters)


# ---------- UPDATE ----------

@users_router.patch("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user_profile(
    data: UserUpdateProfile,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    user_service: Annotated[
        UserService,
        Depends(get_user_service),
    ],
):
    return await user_service.update_user_profile(
        current_user=current_user,
        data=data,
    )


# ---------- DELETE ----------

@users_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_admin(
    user_id: int,
    _: Annotated[
        User,
        Depends(get_current_admin),
    ],
    user_service: Annotated[
        UserService,
        Depends(get_user_service),
    ],
):
    return await user_service.delete_user_by_id(user_id)