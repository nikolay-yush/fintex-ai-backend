from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.features.categories.repositories  import CategoriesRepository
from app.features.categories.schemas import CategoryCreate, CategoryUpdate, CategoriesFilters
from app.features.categories.models import Category
from app.features.wallets.repository import WalletsRepository


class CategoriesService:
    def __init__(
        self,
        db_async_session: AsyncSession,
        categories_repo: CategoriesRepository,
        wallets_repo: WalletsRepository,
    ) -> None:
        self._db_async_session = db_async_session
        self._categories_repo = categories_repo
        self._wallets_repo = wallets_repo

    async def _verify_wallet_ownership(self, wallet_id: int, user_id: int) -> None:
        """Helper to check if the wallet exists and belongs to the user."""
        wallet = await self._wallets_repo.get_wallet_by_id_and_user(wallet_id=wallet_id, user_id=user_id)
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found or access denied",
            )

    async def get_categories(
        self, wallet_id: int, user_id: int, filters: CategoriesFilters
    ) -> tuple[list[Category], int]:
        """Get filtered and paginated list of categories for a specific wallet belonging to the user."""
        await self._verify_wallet_ownership(wallet_id=wallet_id, user_id=user_id)
        return await self._categories_repo.get_categories_by_filters(wallet_id=wallet_id, filters=filters)

    async def get_category_by_id(self, category_id: int, wallet_id: int, user_id: int) -> Category:
        """Get a specific category ensuring ownership through the wallet."""
        await self._verify_wallet_ownership(wallet_id=wallet_id, user_id=user_id)
        
        category = await self._categories_repo.get_category_by_id_and_wallet(
            category_id=category_id, wallet_id=wallet_id
        )
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found in this wallet",
            )
        return category

    async def create_category(self, wallet_id: int, user_id: int, data: CategoryCreate) -> Category | None:
        """Create a new category within a verified wallet."""
        await self._verify_wallet_ownership(wallet_id=wallet_id, user_id=user_id)

        category_data = data.model_dump()
        category_data["wallet_id"] = wallet_id

        try:
            category = await self._categories_repo.create_category(category_data)
            await self._db_async_session.commit()
            await self._db_async_session.refresh(category)
            return category
        
        except IntegrityError:
            await self._db_async_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists in the wallet",
            )

    async def update_category(
        self, category_id: int, wallet_id: int, user_id: int, data: CategoryUpdate
    ) -> Category | None:
        """Update category details with strict ownership and existence verification."""
        category = await self.get_category_by_id(
            category_id=category_id, wallet_id=wallet_id, user_id=user_id
        )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return category

        try:
            updated_category = await self._categories_repo.update_category(category_id, update_data)
            await self._db_async_session.commit()
            await self._db_async_session.refresh(updated_category)
            return updated_category
        
        except IntegrityError:
            await self._db_async_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists in the wallet",
            )

    async def delete_category(self, category_id: int, wallet_id: int, user_id: int) -> bool:
        """Delete category with ownership verification."""
        await self.get_category_by_id(
            category_id=category_id, wallet_id=wallet_id, user_id=user_id
        )

        await self._categories_repo.delete_category(category_id)
        await self._db_async_session.commit()
        return True