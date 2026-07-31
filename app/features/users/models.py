from __future__ import annotations
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from pydantic import BaseModel
from sqlalchemy import (
    CheckConstraint,
    String,
    DateTime,
    Numeric,
    Boolean,
    ForeignKey,
    UniqueConstraint,
    func,
    Enum as SQLEnum,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.features.auth.models import EmailVerificationToken
from app.shared.base_model import BaseCRUDModel
from app.features.users.enums import UserRole


class User(BaseCRUDModel):
    """Model representing a user in the system."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True, 
        nullable=False, 
        index=True
    )
    email_verified: Mapped[bool] = mapped_column(
        Boolean, 
        server_default=text("false"), 
        nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(512), 
        nullable=False
    )
    full_name: Mapped[str] = mapped_column(
        String(150), 
        nullable=False
    )
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role_enum"),
        default=UserRole.USER,
        nullable=False,
    )
    # Can used by the system users for soft deletion or deactivation of accounts.
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        server_default=text("true"), 
        nullable=False
    )
    is_banned: Mapped[bool] = mapped_column(
        Boolean,
        server_default=text("false"),
        nullable=False,
    )
    ban_reason: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    # The last time the user logged in. Checking for suspicious activites.
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    # Updated periodically when the user interacts with the system.
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )

    email_verification_token: Mapped[
        "EmailVerificationToken | None"
    ] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    
