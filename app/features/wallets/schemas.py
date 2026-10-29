from datetime import datetime
from decimal import Decimal
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.features.wallets.models import WalletType


class WalletResponse(BaseModel):
    """Schema for returning wallet data to the client."""
    id: int
    user_id: int
    name: str
    type: WalletType
    balance: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WalletListResponse(BaseModel):
    """Paginated response wrapper for a list of wallets."""
    wallets: List[WalletResponse]
    total: int
    skip: int
    limit: int

class WalletCreate(BaseModel):
    """Schema for creating a new wallet. 
    Balance is excluded as it defaults to 0 on creation.
    """
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Wallet name (e.g., 'Cash' or 'Main Card')",
        examples=["Main Card"],
    )
    type: WalletType = Field(
        ...,
        description="Wallet type: SAVINGS or SPENDINGS",
        examples=[WalletType.SPENDINGS],
    )


class WalletUpdate(BaseModel):
    """Schema for updating wallet details. 
    Balance cannot be modified here (only through transactions).
    """
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="New wallet name",
    )
    type: Optional[WalletType] = Field(
        None,
        description="New wallet type",
    )


class WalletsFilters(BaseModel):
    """Filtering, sorting, and pagination parameters for the wallet list."""

    # --- Search / Text filters ---
    name: Optional[str] = Field(
        default=None,
        description="Filter by wallet name (supports substring search)",
    )

    # --- Type & Balance filters ---
    type: Optional[WalletType] = Field(
        default=None,
        description="Filter by wallet type (SAVINGS or SPENDINGS)",
    )
    balance_min: Optional[Decimal] = Field(
        default=None,
        ge=Decimal("0"),
        description="Minimum wallet balance",
    )
    balance_max: Optional[Decimal] = Field(
        default=None,
        ge=Decimal("0"),
        description="Maximum wallet balance",
    )

    # --- Creation dates ---
    created_from: Optional[datetime] = Field(
        default=None,
        description="Filter wallets created from this timestamp",
    )
    created_to: Optional[datetime] = Field(
        default=None,
        description="Filter wallets created up to this timestamp",
    )

    # --- Update dates ---
    updated_from: Optional[datetime] = Field(
        default=None,
        description="Filter wallets updated from this timestamp",
    )
    updated_to: Optional[datetime] = Field(
        default=None,
        description="Filter wallets updated up to this timestamp",
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
    sort_by: Optional[Literal["name", "balance", "created_at", "updated_at"]] = Field(
        default=None,
        description="Field to sort by ('name', 'balance', 'created_at', 'updated_at')",
    )
    sort_order: Literal["asc", "desc"] = Field(
        default="asc",
        description="Sort order: 'asc' for ascending, 'desc' for descending",
    )

