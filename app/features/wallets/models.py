from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List

from sqlalchemy import (
    CheckConstraint,
    String,
    DateTime,
    Numeric,
    ForeignKey,
    func,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.base_crud import BaseCRUDModel
from app.features.wallets.enums import WalletType


if TYPE_CHECKING:
    from app.features.users.models import User
    # from app.features.categories.models import Category
    # from app.features.transactions.models import Transaction


class Wallet(BaseCRUDModel):
    """User's financial wallet (Bank Card)"""

    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[WalletType] = mapped_column(
        SQLEnum(WalletType, name="wallet_type_enum", native_enum=True), 
        nullable=False
    )
    balance: Mapped[Decimal] = mapped_column(
        Numeric(20, 2), server_default="0", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship(
        "User",
        back_populates="wallets",
    )

    categories: Mapped[List["Category"]] = relationship(  # type: ignore
        "Category",
        back_populates="wallet",
        cascade="all, delete-orphan",
        lazy="noload",
    )
    transactions: Mapped[List["Transaction"]] = relationship(  # type: ignore
        "Transaction",
        back_populates="wallet",
        cascade="all, delete-orphan",
        lazy="noload",
    )
    
    __table_args__ = (
        CheckConstraint("balance >= 0", name="ck_wallet_balance_non_negative"),
    )