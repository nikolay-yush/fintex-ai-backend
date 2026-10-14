from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.categories.models import Category  
from app.features.categories.schemas import CategoriesFilters  
from app.shared.base_crud import BaseCRUD


class CategoriesRepository(BaseCRUD[Category]):

    def __init__(self, db_async_session: AsyncSession) -> None:
        super().__init__(db_async_session=db_async_session, model=Category)

    async def get_category_by_id_and_wallet(
        self, category_id: int, wallet_id: int
    ) -> Category | None:
        """Get a specific category ensuring it belongs to the wallet."""
        query = select(self._model).where(
            self._model.id == category_id,
            self._model.wallet_id == wallet_id,
        )
        result = await self._db_async_session.execute(query)
        return result.scalar_one_or_none()

    async def get_categories_by_filters(
        self,
        wallet_id: int,
        filters: CategoriesFilters,
    ) -> tuple[list[Category], int]:
        """Get paginated and filtered list of categories for a specific wallet."""
        query = select(Category).where(Category.wallet_id == wallet_id)

        # --- Filters ---
        if filters.name is not None:
            query = query.where(Category.name.ilike(f"%{filters.name}%"))

        if filters.current_budget_limit_min is not None:
            query = query.where(Category.current_budget_limit >= filters.current_budget_limit_min)

        if filters.current_budget_limit_max is not None:
            query = query.where(Category.current_budget_limit <= filters.current_budget_limit_max)

        if filters.created_from is not None:
            query = query.where(Category.created_at >= filters.created_from)

        if filters.created_to is not None:
            query = query.where(Category.created_at <= filters.created_to)

        if filters.updated_from is not None:
            query = query.where(Category.updated_at >= filters.updated_from)

        if filters.updated_to is not None:
            query = query.where(Category.updated_at <= filters.updated_to)

        # --- Total count subquery ---
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self._db_async_session.execute(count_query)
        total = count_result.scalar_one() or 0

        # --- Sorting ---
        if filters.sort_by is not None:
            sort_column = getattr(Category, filters.sort_by, None)
            if sort_column is not None:
                if filters.sort_order == "desc":
                    query = query.order_by(sort_column.desc())
                else:
                    query = query.order_by(sort_column.asc())
        else:
            # Default sorting
            query = query.order_by(Category.id.desc())

        # --- Pagination ---
        query = query.offset(filters.skip)
        query = query.limit(filters.limit)

        result = await self._db_async_session.execute(query)
        categories = list(result.scalars().all())

        return categories, total

    async def create_category(self, data: dict[str, Any]) -> Category | None:
        return await super().create_one(data)

    async def update_category(
        self, category_id: int, data: dict[str, Any]
    ) -> Category | None:
        return await super().update_one(category_id, data)

    async def delete_category(self, category_id: int) -> Category | None:
        return await super().delete_one(category_id)