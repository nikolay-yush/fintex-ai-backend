from typing import Annotated
from fastapi import APIRouter, Depends, Path, Request, status

from app.core.security.rate_limit import rate_limit 

from app.features.auth.dependencies import get_current_user
from app.features.users.models import User
from app.features.wallets.dependencies import get_wallets_service
from app.features.wallets.service import WalletsService
from app.features.wallets.schemas import (
    WalletCreate,
    WalletListResponse,
    WalletRead,
    WalletUpdate,
    WalletsFilters,
)

wallets_router = APIRouter(
    prefix="/wallets",
    tags=["Wallets"],
)


@wallets_router.get(
    "",
    response_model=WalletListResponse,
    summary="Get all user's wallets",
)
@rate_limit(max_requests=20, window_seconds=20, key_prefix="get_wallets")
async def get_wallets(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    wallet_service: Annotated[WalletsService, Depends(get_wallets_service)],
    filters: Annotated[WalletsFilters, Depends()],
):
    """Get a paginated and filtered list of wallets for the current user."""
    items, total = await wallet_service.get_wallets(
        user_id=current_user.id, filters=filters
    )
    return {
        "items": items,
        "total": total,
        "skip": filters.skip,
        "limit": filters.limit,
    }


@wallets_router.get(
    "/{wallet_id}",
    response_model=WalletRead,
    summary="Get a specific wallet",
)
@rate_limit(max_requests=20, window_seconds=20, key_prefix="get_wallet_detail")
async def get_wallet(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    wallet_service: Annotated[WalletsService, Depends(get_wallets_service)],
    wallet_id: int = Path(..., ge=1, description="The ID of the wallet"),
):
    """Get a specific wallet by ID, ensuring user ownership."""
    wallet = await wallet_service.get_wallet_by_id(
        wallet_id=wallet_id, user_id=current_user.id
    )
    return wallet


@wallets_router.post(
    "",
    response_model=WalletRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new wallet",
)
@rate_limit(max_requests=5, window_seconds=60, key_prefix="create_wallet")
async def create_wallet(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    wallet_service: Annotated[WalletsService, Depends(get_wallets_service)],
    data: WalletCreate,
):
    """Create a new wallet with a default zero balance for the current user."""
    return await wallet_service.create_wallet(user_id=current_user.id, data=data)


@wallets_router.patch(
    "/{wallet_id}",
    response_model=WalletRead,
    summary="Update wallet details",
)
@rate_limit(max_requests=10, window_seconds=60, key_prefix="update_wallet")
async def update_wallet(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    wallet_service: Annotated[WalletsService, Depends(get_wallets_service)],
    data: WalletUpdate,
    wallet_id: int = Path(..., ge=1),
    
):
    """Update wallet properties (name or type). Balance cannot be modified here."""
    wallet = await wallet_service.update_wallet(
        wallet_id=wallet_id, user_id=current_user.id, data=data
    )
    return wallet


@wallets_router.delete(
    "/{wallet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a wallet",
)
@rate_limit(max_requests=5, window_seconds=60, key_prefix="delete_wallet")
async def delete_wallet(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    wallet_service: Annotated[WalletsService, Depends(get_wallets_service)],
    wallet_id: int = Path(..., ge=1),
):
    """Delete a wallet and cascade delete its related data."""
    await wallet_service.delete_wallet(
        wallet_id=wallet_id, user_id=current_user.id
    )
    return None