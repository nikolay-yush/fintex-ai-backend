from typing import Annotated
from fastapi import APIRouter, Depends, Path, Request, status

from app.core.security.rate_limit import rate_limit 

from app.features.auth.dependencies import get_current_user
from app.features.users.models import User
from app.features.categories.dependencies import get_categories_service
from app.features.categories.service import CategoriesService
from app.features.categories.schemas import (
    CategoryCreate,
    CategoryListResponse,
    CategoryRead,
    CategoryUpdate,
    CategoriesFilters,
)

categories_router = APIRouter(
    prefix="/wallets/{wallet_id}/categories",
    tags=["Categories"],
)


@categories_router.get(
    "",
    response_model=CategoryListResponse,
    summary="Get all categories for a specific wallet",
)
@rate_limit(max_requests=20, window_seconds=20, key_prefix="get_categories")
async def get_categories(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    category_service: Annotated[CategoriesService, Depends(get_categories_service)],
    filters: Annotated[CategoriesFilters, Depends()],
    wallet_id: int = Path(..., ge=1, description="The ID of the wallet"),
):
    """Get a paginated and filtered list of categories for a specific wallet belonging to the user."""
    items, total = await category_service.get_categories(
        wallet_id=wallet_id, user_id=current_user.id, filters=filters
    )
    return {
        "items": items,
        "total": total,
        "skip": filters.skip,
        "limit": filters.limit,
    }


@categories_router.get(
    "/{category_id}",
    response_model=CategoryRead,
    summary="Get a specific category",
)
@rate_limit(max_requests=20, window_seconds=20, key_prefix="get_category_detail")
async def get_category(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    category_service: Annotated[CategoriesService, Depends(get_categories_service)],
    wallet_id: int = Path(..., ge=1, description="The ID of the wallet"),
    category_id: int = Path(..., ge=1, description="The ID of the category"),
):
    """Get a specific category by ID, ensuring ownership through the wallet."""
    category = await category_service.get_category_by_id(
        category_id=category_id, wallet_id=wallet_id, user_id=current_user.id
    )
    return category


@categories_router.post(
    "",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category in a wallet",
)
@rate_limit(max_requests=10, window_seconds=60, key_prefix="create_category")
async def create_category(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    category_service: Annotated[CategoriesService, Depends(get_categories_service)],
    data: CategoryCreate,
    wallet_id: int = Path(..., ge=1, description="The ID of the wallet"),
):
    """Create a new financial category for the specified wallet."""
    return await category_service.create_category(
        wallet_id=wallet_id, user_id=current_user.id, data=data
    )


@categories_router.patch(
    "/{category_id}",
    response_model=CategoryRead,
    summary="Update category details",
)
@rate_limit(max_requests=10, window_seconds=60, key_prefix="update_category")
async def update_category(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    category_service: Annotated[CategoriesService, Depends(get_categories_service)],
    data: CategoryUpdate,
    wallet_id: int = Path(..., ge=1, description="The ID of the wallet"),
    category_id: int = Path(..., ge=1, description="The ID of the category"),
):
    """Update category properties (name, notation, or budget limit)."""
    category = await category_service.update_category(
        category_id=category_id, wallet_id=wallet_id, user_id=current_user.id, data=data
    )
    return category


@categories_router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a category",
)
@rate_limit(max_requests=5, window_seconds=60, key_prefix="delete_category")
async def delete_category(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    category_service: Annotated[CategoriesService, Depends(get_categories_service)],
    wallet_id: int = Path(..., ge=1, description="The ID of the wallet"),
    category_id: int = Path(..., ge=1, description="The ID of the category"),
):
    """Delete a category and its associated transaction mappings."""
    await category_service.delete_category(
        category_id=category_id, wallet_id=wallet_id, user_id=current_user.id
    )
    return None