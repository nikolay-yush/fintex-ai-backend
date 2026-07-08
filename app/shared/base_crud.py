from typing import Any, TypeVar

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Generic

from app.shared.base_model import BaseCRUDModel


ModelCRUD = TypeVar("ModelCRUD", bound=BaseCRUDModel)


class BaseCRUD(Generic[ModelCRUD]):
    """
        Base CRUD class.
            get_one_by_id - get one model by id.
            create_one - create one model.
            update_one - update one model.
            delete_one - delete one model.
    """
    def __init__(self, db: AsyncSession, model: type[ModelCRUD]) -> None:
        """
        Args:
            db (AsyncSession): The database session.
            model (type[ModelCRUD]): The model class.
        """
        self._db = db
        self._model = model

    async def get_one_by_id(self, model_id: int) -> ModelCRUD | None:
        query = select(self._model).where(self._model.id == model_id)
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def create_one(self, data: dict[str, Any]) -> ModelCRUD | None:
        result = await self._db.execute(
            insert(self._model)
            .values(**data)
            .returning(self._model)
        )
        return result.scalar_one_or_none()

    async def update_one(self, model_id: int, data: dict[str, Any]) -> ModelCRUD | None:
        result = await self._db.execute(
            update(self._model)
            .where(self._model.id == model_id)
            .values(**data)
            .returning(self._model)
        )
        return result.scalar_one_or_none()

    async def delete_one(self, model_id: int) -> ModelCRUD | None:
        result = await self._db.execute(
            delete(self._model)
            .where(self._model.id == model_id)
            .returning(self._model)
        )
        return result.scalar_one_or_none()