from fastapi import APIRouter

from app.features.auth.router import auth_router
from app.features.users.router import users_router


api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(users_router)