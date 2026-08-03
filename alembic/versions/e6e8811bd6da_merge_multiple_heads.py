"""merge multiple heads

Revision ID: e6e8811bd6da
Revises: 3fe31eeba01a
Create Date: 2026-08-02 21:14:44.708007

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6e8811bd6da'
down_revision: Union[str, Sequence[str], None] = '3fe31eeba01a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
