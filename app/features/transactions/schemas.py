from datetime import datetime
from decimal import Decimal
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.features.transactions.models import TransactionType, RecurrenceInterval


class TransactionCreate(BaseModel):
    """Schema for creating a new transaction.
    wallet_id and transfer_pair_id/idempotency handling can be managed in service or request.
    """
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Transaction name or description (e.g., 'Coffee' or 'Salary')",
        examples=["Groceries in supermarket"],
    )
    type: TransactionType = Field(
        ...,
        description="Transaction type: INCOME or EXPENSE",
        examples=[TransactionType.EXPENSE],
    )
    notation: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional detailed note",
    )
    amount: Decimal = Field(
        ...,
        gt=Decimal("0"),
        description="Transaction amount (must be greater than 0)",
        examples=[Decimal("150.50")],
    )
    category_id: int = Field(
        ...,
        ge=1,
        description="ID of the category associated with this transaction",
    )
    idempotency_key: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="Unique key to prevent duplicate transaction creation",
        examples=["uuid-or-client-side-unique-hash"],
    )
    recurrence_interval: RecurrenceInterval = Field(
        default=RecurrenceInterval.NEVER,
        description="Recurrence frequency: NEVER, DAILY, WEEKLY, MONTHLY, YEARLY",
    )
    recurrence_date: Optional[datetime] = Field(
        default=None,
        description="Date for the next recurrence (required if recurrence_interval is not NEVER)",
    )


class TransactionUpdate(BaseModel):
    """Schema for updating transaction details."""
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="New transaction name",
    )
    notation: Optional[str] = Field(
        None,
        max_length=500,
        description="New note",
    )
    amount: Optional[Decimal] = Field(
        None,
        gt=Decimal("0"),
        description="New amount",
    )
    category_id: Optional[int] = Field(
        None,
        ge=1,
        description="New category ID",
    )
    recurrence_interval: Optional[RecurrenceInterval] = Field(
        None,
        description="New recurrence interval",
    )
    recurrence_date: Optional[datetime] = Field(
        None,
        description="New recurrence date",
    )


class TransactionRead(BaseModel):
    """Schema for returning transaction data to the client."""
    id: int
    wallet_id: int
    category_id: int
    transfer_pair_id: Optional[int]
    name: str
    type: TransactionType
    notation: Optional[str]
    amount: Decimal
    recurrence_interval: RecurrenceInterval
    recurrence_date: Optional[datetime]
    idempotency_key: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionsFilters(BaseModel):
    """Filtering, sorting, and pagination parameters for the transaction list."""

    # --- Search / Text filters ---
    name: Optional[str] = Field(
        default=None,
        description="Filter by transaction name (supports substring search)",
    )

    # --- Specific filters ---
    type: Optional[TransactionType] = Field(
        default=None,
        description="Filter by transaction type (INCOME or EXPENSE)",
    )
    category_id: Optional[int] = Field(
        default=None,
        ge=1,
        description="Filter by category ID",
    )
    recurrence_interval: Optional[RecurrenceInterval] = Field(
        default=None,
        description="Filter by recurrence interval",
    )

    # --- Amount range ---
    amount_min: Optional[Decimal] = Field(
        default=None,
        gt=Decimal("0"),
        description="Minimum transaction amount",
    )
    amount_max: Optional[Decimal] = Field(
        default=None,
        gt=Decimal("0"),
        description="Maximum transaction amount",
    )

    # --- Creation dates ---
    created_from: Optional[datetime] = Field(
        default=None,
        description="Filter transactions created from this timestamp",
    )
    created_to: Optional[datetime] = Field(
        default=None,
        description="Filter transactions created up to this timestamp",
    )

    # --- Pagination ---
    skip: int = Field(
        default=0,
        ge=0,
        description="Number of records to skip for pagination",
    )
    limit: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of records per page",
    )

    # --- Sorting ---
    sort_by: Optional[Literal["name", "amount", "created_at", "updated_at", "type"]] = Field(
        default=None,
        description="Field to sort by",
    )
    sort_order: Literal["asc", "desc"] = Field(
        default="desc",
        description="Sort order: 'asc' for ascending, 'desc' for descending (default newest first)",
    )


class TransactionListResponse(BaseModel):
    """Paginated response wrapper for a list of transactions."""
    items: List[TransactionRead]
    total: int
    skip: int
    limit: int