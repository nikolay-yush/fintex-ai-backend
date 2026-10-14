from datetime import datetime
from decimal import Decimal
from typing import Optional
from enum import Enum

from sqlalchemy import (
    String,
    DateTime,
    Numeric,
    func,
    ForeignKey,
    Index,
    Enum as SQLEnum,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import BaseCRUDModel
from app.features.transactions.enums import TransactionType, RecurrenceInterval




class Transaction(BaseCRUDModel):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[TransactionType] = mapped_column(
        SQLEnum(TransactionType, name="transaction_type_enum", native_enum=False),
        nullable=False,
    )
    notation: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    recurrence_interval: Mapped[RecurrenceInterval] = mapped_column(
        SQLEnum(RecurrenceInterval, name="transaction_recurrence_interval_enum", native_enum=False),
        server_default=RecurrenceInterval.NEVER.value,
        nullable=False,
    )
    recurrence_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),  # ORM-level
        nullable=False,
    )

    # --- IDEMPOTENCY ---
    idempotency_key: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    # --- FOREIGN KEYS ---
    wallet_id: Mapped[int] = mapped_column(
        ForeignKey("wallets.id", ondelete="CASCADE"),
        nullable=False,
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
    )
    transfer_pair_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("transactions.id", ondelete="SET NULL"),
        nullable=True,
    )

    # --- RELATIONSHIPS ---
    wallet: Mapped["Wallet"] = relationship(  # type: ignore
        "Wallet",
        back_populates="transactions",
        lazy="noload",
    )

    category: Mapped["Category"] = relationship(  # type: ignore
        "Category",
        back_populates="transactions",
        lazy="noload",
    )

    transfer_pair: Mapped[Optional["Transaction"]] = relationship(
        "Transaction",
        foreign_keys=[transfer_pair_id],
        remote_side=[id],
        post_update=True,  # prevent circular FK
    )

    # --- CONSTRAINTS & INDEXES ---
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_tx_amount_positive"),
        CheckConstraint(
            "transfer_pair_id IS NULL OR transfer_pair_id != id",
            name="ck_tx_not_self_link",
        ),
        CheckConstraint(
            "(recurrence_interval = 'NEVER') OR (recurrence_date IS NOT NULL)",
            name="ck_tx_recurrence_date",
        ),
        UniqueConstraint(
            "wallet_id",
            "idempotency_key",
            name="uq_wallet_idempotency_key",
        ),
        Index("ix_transactions_wallet_id", "wallet_id"),
        Index("ix_transactions_category_id", "category_id"),
    )