from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import (
    String,
    DateTime,
    Numeric,
    UniqueConstraint,
    func,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import BaseCRUDModel


class Category(BaseCRUDModel):
    ''' Category financial operations'''
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    notation: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Current budget limit for the category
    current_budget_limit: Mapped[Decimal] = mapped_column(
        Numeric(20, 2), server_default="0.00", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )

    # --- Foreign Keys ---
    wallet_id: Mapped[int] = mapped_column(
        ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False
    )

    # --- Relationships ---
    wallet: Mapped["Wallet"] = relationship(  # type: ignore
        "Wallet", 
        back_populates="categories",
        lazy="noload"
    )
    transactions: Mapped[List["Transaction"]] = relationship( # type: ignore
        "Transaction",
        back_populates="category",
        cascade="all, delete-orphan",
        lazy="noload"
    )

    __table_args__ = (
        UniqueConstraint(
            "wallet_id",
            "name",
            name="uq_category_wallet_name",
        ),
        CheckConstraint("current_budget_limit >= 0", name="ck_category_current_budget_limit_non_negative"),
    )