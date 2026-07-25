from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.features.auth.dependencies import get_auth_service
from app.features.auth.schemas import (
    TokenResponse,
    UserLogin,
    UserRegister,
)
from app.features.auth.service import AuthService
from app.features.users.schemas import UserResponse


auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserRegister,
    auth_service: Annotated[
        AuthService,
        Depends(get_auth_service),
    ],
):
    return await auth_service.register(data)

@auth_router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    data: UserLogin,
    auth_service: Annotated[
        AuthService,
        Depends(get_auth_service),
    ],
):
    return await auth_service.login(data)