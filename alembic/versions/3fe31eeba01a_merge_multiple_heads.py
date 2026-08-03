"""merge multiple heads

Revision ID: 3fe31eeba01a
Revises: 48f81725b6c6, ff6973e4ebbc
Create Date: 2026-08-02 21:13:26.120506

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3fe31eeba01a'
down_revision: Union[str, Sequence[str], None] = ('48f81725b6c6', 'ff6973e4ebbc')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
