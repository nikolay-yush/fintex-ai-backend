from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.postgres.base import Base
from app.shared.base_model import BaseCRUDModel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.features.users.models import User


class EmailVerificationToken(BaseCRUDModel):
    __tablename__ = "email_verification_tokens"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        nullable=False,
    )

    user: Mapped["User"] = relationship()