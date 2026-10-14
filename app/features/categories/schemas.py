from datetime import datetime
from decimal import Decimal
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    """Schema for creating a new category.
    wallet_id is passed via the URL path, so it's excluded here.
    """
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Category name (e.g., 'Groceries' or 'Transport')",
        examples=["Groceries"],
    )
    notation: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional description or notation for the category",
        examples=["Supermarket shopping expenses"],
    )
    current_budget_limit: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0"),
        description="Current budget limit for the category",
        examples=[Decimal("500.00")],
    )


class CategoryUpdate(BaseModel):
    """Schema for updating category details."""
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="New category name",
    )
    notation: Optional[str] = Field(
        None,
        max_length=500,
        description="New notation or description",
    )
    current_budget_limit: Optional[Decimal] = Field(
        None,
        ge=Decimal("0"),
        description="New budget limit",
    )


class CategoryRead(BaseModel):
    """Schema for returning category data to the client."""
    id: int
    wallet_id: int
    name: str
    notation: Optional[str]
    current_budget_limit: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoriesFilters(BaseModel):
    """Filtering, sorting, and pagination parameters for the category list."""

    # --- Search / Text filters ---
    name: Optional[str] = Field(
        default=None,
        description="Filter by category name (supports substring search)",
    )

    # --- Budget limit filters ---
    current_budget_limit_min: Optional[Decimal] = Field(
        default=None,
        ge=Decimal("0"),
        description="Minimum budget limit",
    )
    current_budget_limit_max: Optional[Decimal] = Field(
        default=None,
        ge=Decimal("0"),
        description="Maximum budget limit",
    )

    # --- Creation dates ---
    created_from: Optional[datetime] = Field(
        default=None,
        description="Filter categories created from this timestamp",
    )
    created_to: Optional[datetime] = Field(
        default=None,
        description="Filter categories created up to this timestamp",
    )

    # --- Update dates ---
    updated_from: Optional[datetime] = Field(
        default=None,
        description="Filter categories updated from this timestamp",
    )
    updated_to: Optional[datetime] = Field(
        default=None,
        description="Filter categories updated up to this timestamp",
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
    sort_by: Optional[Literal["name", "current_budget_limit", "created_at", "updated_at"]] = Field(
        default=None,
        description="Field to sort by ('name', 'current_budget_limit', 'created_at', 'updated_at')",
    )
    sort_order: Literal["asc", "desc"] = Field(
        default="asc",
        description="Sort order: 'asc' for ascending, 'desc' for descending",
    )


class CategoryListResponse(BaseModel):
    """Paginated response wrapper for a list of categories."""
    items: List[CategoryRead]
    total: int
    skip: int
    limit: int