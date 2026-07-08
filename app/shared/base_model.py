from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from app.core.db.postgres.base import Base

class BaseCRUDModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )